# Flux Views (arm)

GitHub actions was too slow, so instead we will use an hpc7g (arm) 4xlarge instance to build. I create one in the console.

## Final Images

| Name | Repository | Tags |
|------|------------|------|
| ghcr.io/rse-ops/lammps-arm | [ghcr.io/rse-ops/lammps-arm](https://github.com/orgs/rse-ops/packages/container/package/lammps-arm) | rocky-9, ubuntu-jammy |
| ghcr.io/rse-ops/laghos-arm | [ghcr.io/rse-ops/laghos-arm](https://github.com/orgs/rse-ops/packages/container/package/laghos-arm) | ubuntu-jammy |
| ghcr.io/rse-ops/amg-arm | [ghcr.io/rse-ops/amg-arm](https://github.com/orgs/rse-ops/packages/container/package/amg-arm) | ubuntu-jammy |
| ghcr.io/converged-computing/flux-view-rocky | [ghcr.io/converged-computing/flux-view-rocky](https://github.com/converged-computing/flux-views/pkgs/container/flux-view-rocky) | arm-8, arm-9 | 
| ghcr.io/converged-computing/flux-view-ubuntu | [ghcr.io/converged-computing/flux-view-ubuntu](https://github.com/converged-computing/flux-views/pkgs/container/flux-view-ubuntu) | arm-focal, arm-jammy |

## Building

Shell into the instance with your PEM:

```bash
ssh -o 'IdentitiesOnly yes' -i path-to-key.pem ec2-user@ec2-xx-xx-xx-xx.compute-1.amazonaws.com
```

And then install docker and update:

```bash
sudo yum update -y
sudo yum install -y docker
sudo systemctl start docker
sudo usermod -aG docker $USER
sudo setfacl --modify user:ec2-user:rw /var/run/docker.sock
```

At this point give it a test!

```bash
docker run hello-world
```

If that works, we are good to build here. Let's run this in a screen because we can expect our credential to expire or otherwise get kicked off.

```bash
sudo yum install -y screen
screen
```

The above is very important, as it's likely to cut / freeze at some point and you'll regret it if you don't :) 
Clone the repository:

```bash
sudo yum install -y git
git clone https://github.com/converged-computing/flux-views
```

The default cpu arch is already set to arm, so we don't need to set the build arg. Here are the following builds we need to do.

```bash
# Builds (rocky)
docker buildx build --build-arg tag=8 --build-arg ARCH=aarch64 -f rocky/Dockerfile --platform linux/arm64 --tag ghcr.io/converged-computing/flux-view-rocky:arm-8 ./rocky
docker buildx build --build-arg tag=9 --build-arg ARCH=aarch64 -f rocky/Dockerfile --platform linux/arm64 --tag ghcr.io/converged-computing/flux-view-rocky:arm-9 ./rocky

# without the arch
docker build --build-arg tag=8 --network host --build-arg ARCH=aarch64 -f rocky/Dockerfile --tag ghcr.io/converged-computing/flux-view-rocky:arm-8 ./rocky
docker build --build-arg tag=9 --network host --build-arg ARCH=aarch64 -f rocky/Dockerfile --tag ghcr.io/converged-computing/flux-view-rocky:arm-9 ./rocky

# Builds (ubuntu) - skipping bionic
docker buildx build --build-arg tag=focal --build-arg ARCH=aarch64 -f ubuntu/Dockerfile --platform linux/arm64 --tag ghcr.io/converged-computing/flux-view-ubuntu:arm-focal ./ubuntu
docker buildx build --build-arg tag=jammy --build-arg ARCH=aarch64 -f ubuntu/Dockerfile --platform linux/arm64 --tag ghcr.io/converged-computing/flux-view-ubuntu:arm-jammy ./ubuntu

# If you are on an arm instance, skip the the buildx and platform
docker build --build-arg tag=focal --network host --build-arg ARCH=aarch64 -f ubuntu/Dockerfile --tag ghcr.io/converged-computing/flux-view-ubuntu:arm-focal ./ubuntu
docker build --build-arg tag=jammy --network host --build-arg ARCH=aarch64 -f ubuntu/Dockerfile --tag ghcr.io/converged-computing/flux-view-ubuntu:arm-jammy ./ubuntu

# And for the lammps builds here
docker buildx build -f arm/Dockerfile.ubuntu-lammps --platform linux/arm64 --tag ghcr.io/rse-ops/lammps-arm:ubuntu-jammy ./arm
docker buildx build -f arm/Dockerfile.rocky-lammps --platform linux/arm64 --tag ghcr.io/rse-ops/lammps-arm:rocky-9 ./arm
docker buildx build -f arm/Dockerfile.ubuntu-amg --platform linux/arm64 --tag ghcr.io/rse-ops/amg-arm:ubuntu-jammy ./arm
docker buildx build -f arm/Dockerfile.ubuntu-laghos --platform linux/arm64 --tag ghcr.io/rse-ops/laghos-arm:ubuntu-jammy ./arm
docker build -f arm/Dockerfile.ubuntu-amg-2023 --platform linux/arm64 --tag ghcr.io/rse-ops/amg-2023-arm:ubuntu-jammy ./arm

# Pushes (ensure you have a credential for the registry)
docker push ghcr.io/converged-computing/flux-view-rocky:arm-8
docker push ghcr.io/converged-computing/flux-view-rocky:arm-9
docker push ghcr.io/converged-computing/flux-view-ubuntu:arm-focal
docker push ghcr.io/converged-computing/flux-view-ubuntu:arm-jammy

# LAMMPS
docker push ghcr.io/rse-ops/lammps-arm:rocky-9
docker push ghcr.io/rse-ops/lammps-arm:ubuntu-jammy

# Other apps (ubuntu only)
docker push ghcr.io/rse-ops/amg-arm:ubuntu-jammy
docker push ghcr.io/rse-ops/laghos-arm:ubuntu-jammy
```

And that's it! You can exit and delete the instance.
