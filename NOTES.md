# Setup

## Create 3 k3d clusters
- 1 Global control plane cluster
- 2 remote clusters

## Install Kuma in multi-zone configuration 

- Install Kuma
- Install ZoneIngress on the 2 zonal clusters
- MUST enable mTLS for cross-zone communication + traffic permission policy

## Verify Kuma Installation

Make sure the current context is the management cluster.

connect to the web UI:

```
kubectl port-forward -n kuma-system svc/kuma-control-plane 5681:5681
```

Then browse to http://localhost:5681

You can also check various REST endpoints like zones:

```
$ curl http://localhost:5681/zones
{
 "total": 2,
 "items": [
  {
   "type": "Zone",
   "name": "remote-cluster-1",
   "creationTime": "2022-01-30T19:30:32Z",
   "modificationTime": "2022-01-30T19:30:32Z",
   "enabled": true
  },
  {
   "type": "Zone",
   "name": "remote-cluster-2",
   "creationTime": "2022-01-30T19:30:54Z",
   "modificationTime": "2022-01-30T19:30:54Z",
   "enabled": true
  }
 ],
 "next": null
}
```

## Install the social graph service and DB

- Install the service, by applying the social-graph.yaml manifest to the remote clusters.

Make sure to switch your kube context to a remote cluster.

Then port-forward to expose the service locally:

```
kubectl port-forward -n delinkcious svc/social-graph-manager 9090:9090
```

Now you can curl this endpoint (or any other name) and get an empty result:

```
$ curl http://localhost:9090/following/gigi
{"following":{},"err":""}
```

## Add the social graph service to Kuma

So far, Kuma is unaware of the social graph service.

The next step is to add the service to Kuma.

The trick is to add an annotation to the namespace and then automagically
Kuma will inject its data proxies to all the pods in the namespace

```
annotations:
    kuma.io/sidecar-injection: enabled
    kuma.io/mesh: default
```

# Enable connectivity between zones

Just injecting the data proxies is not enough for cross-zone connectivity.
Kuma requires that services will have strong identity via mTLS and specific traffic policy

The mTLS policy is defined on the Mesh resource:

Initially the default mesh has no policies:

```
$ kubectl get meshes.kuma.io default -o yaml | kubectl neat
apiVersion: kuma.io/v1alpha1
kind: Mesh
metadata:
  name: default
```

Let's add mTLS across the board using the builtin certificate authority:

```

```






# Reference

https://konghq.com/blog/zerolb/
https://thenewstack.io/zerolb-a-new-decentralized-pattern-for-load-balancing/
https://github.com/svenwal/kuma-multi-zone-k3d/blob/main/start.sh
https://jetzlstorfer.medium.com/running-k3d-and-istio-locally-32adc5c41a63

https://kuma.io/docs/1.4.x/deployments/stand-alone/
https://kuma.io/docs/1.4.x/networking/networking/

https://www.cncf.io/online-programs/multi-cluster-multi-cloud-service-mesh-with-cncfs-kuma-and-envoy/