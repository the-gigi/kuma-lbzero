import tempfile

import logging
import sh
import shutil

import config


def verify_prerequisites():
    """Verif    y the required tools are installed"""

    prerequisites = 'docker kubectl kumactl k3d'.split()
    for prereq in prerequisites:
        if shutil.which(prereq) is None:
            raise RuntimeError('Missing pre-requisite program: ' + prereq)


def get_kds_global_address():
    """
    kubectl get --context $KUMA_GLOBAL -n kuma-system svc kuma-global-zone-sync -o jsonpath='{.status.loadBalancer.ingress[0].ip}'
    """

    json_query = '{.status.loadBalancer.ingress[0].ip}'
    args = f"""--context {config.kube_contexts['management']} -n kuma-system 
                 svc kuma-global-zone-sync 
                 -o jsonpath='{json_query}'""".split()
    kds_global_url = sh.kubectl.get(*args).stdout.decode('utf-8').replace("'", "")
    return f'{kds_global_url}:{config.kds_global_port}'


def install_kuma_component(*args):
    """Run a kumactl command to generate manifests to a fiel and apply them"""
    kuma_manifests_file = tempfile.mktemp() + '.yaml'
    sh.kumactl.install(*args, _out=kuma_manifests_file)
    sh.kubectl.apply('-f', kuma_manifests_file)


def deploy_kuma(kube_context, name, mode):
    """Deploy Kuma into on a Kubernetes cluster

    Depending on the mode it takes different paths
    """
    sh.kubectl.config(['use-context', kube_context])
    logging.info('Installing Kuma on:' + name)

    args = ['control-plane']
    if mode != 'standalone':
        args += ['--mode', mode]
    if mode == 'zone':
        kds_global_address = get_kds_global_address()
        args += f"""--zone {name}
                    --ingress-enabled
                    --kds-global-address 'grpcs://{kds_global_address}""".split()

    print(' '.join(args))
    install_kuma_component(*args)

    # Install Prometheus and Grafana on a standalone or global cluster
    if mode != 'zone':
        logging.info('Installing Prometheus and Grafana')
        install_kuma_component('metrics')

    # Install Kuma DNS on remote clusters
    if mode == 'zone':
        logging.info('Installing Kuma DNS on:' + name)
        install_kuma_component('dns')

    # if mode == 'global':
    #     sh.kumactl.config(f"""control-planes add
    #                           --name zerolb-showcase
    #                           --address http://{kds_global_address}
    #                           --overwrite""".split())


def apply_mesh_policy():
    """Turn on mTLS and metrics"""
    sh.kubectl.apply('-f', 'k8s/mesh.yaml')


def deploy_kuma_multizone():
    """ """
    deploy_kuma(config.kube_contexts['management'], 'management-cluster', 'global')
    deploy_kuma(config.kube_contexts['remote-1'], 'remote-cluster-1', 'zone')
    deploy_kuma(config.kube_contexts['remote-2'], 'remote-cluster-2', 'zone')

    apply_mesh_policy()


def deploy_service(name):
    """Deploy a service to the remote clusters

    All the service Kubernetes resources (Deployment, Service, ServiceAccount, etc)
    must be defined in a single file in the `k8s` directory called `<name>.yaml`

    """
    remote_clusters = 'remote-1 remote-2'.split()
    for cluster in remote_clusters:
        print(f"Deploying the '{name}' service to '{cluster}'")
        args = f'--context {config.kube_contexts[cluster]} -f k8s/{name}.yaml'.split()
        sh.kubectl.apply(*args)


def main():
    logging.basicConfig(level=logging.INFO,
                        format='[%(asctime)s] %(message)s')

    deploy_kuma_multizone()
    deploy_service('social_graph')


if __name__ == '__main__':
    main()
