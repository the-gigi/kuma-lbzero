import logging
import os

import sh


def get_k3d_major_version():
    version = sh.k3d.version().stdout.decode('utf-8')
    major_version = int(version.split('\n')[0].split()[-1][1])
    return major_version

def create_kubeconfig_file(cluster_name):
    kubeconfig = sh.k3d.kubeconfig.get(cluster_name).stdout.decode('utf-8')
    filename = os.path.expanduser(f'~/.kube/config-{cluster_name}')
    open(filename, 'w').write(kubeconfig)
    return filename


def create_k3d_cluster(name, ports):
    """Create a new k3d cluster. Bail out if already exists"""
    clusters = sh.k3d.cluster.list().stdout.decode('utf-8').split('\n')[1:]
    names = [c.split()[0] for c in clusters if c]
    if name in names:
        logging.info(f"The k3d cluster '{name}' already exists")
        return

    version = get_k3d_major_version()
    filter_suffix = ':0' if version == 5 else '[0]'
    disable_traefic = '--disable=traefik@server:0' if version == 5 else '--no-deploy=traefik'

    logging.info('Creating k3d cluster:' + name)
    ports = ' '.join((f"-p {port}@agent{filter_suffix}" for port in ports))

    args = f"""{name}
               --k3s-arg
               {disable_traefic}
               {ports}
               --agents 1
               --verbose""".split()
    sh.k3d.cluster.create(*args)

    kubeconfig_file = create_kubeconfig_file(name)
    logging.info('Kube config file was generated here: ' + kubeconfig_file)

    os.environ['KUBECONFIG'] = kubeconfig_file
    kube_context = 'k3d-' + name
    sh.kubectl.config('use-context', kube_context)

    curr_context = sh.kubectl.config('current-context').stdout.decode('utf-8')[:-1]

    assert (curr_context == kube_context)

