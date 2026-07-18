ARG tag=noble
FROM spack/ubuntu-${tag}:latest AS builder
ARG ARCH=x86_64
ENV ARCH=${ARCH}
ARG FLUX_SCHED_REPO=https://github.com/vsoch/flux-sched
ARG FLUX_SCHED_BRANCH=add-hold

RUN apt-get update && apt-get install -y gettext-base git make pkg-config

# Custom flux-sched branch, built from a local clone via spack `develop`
RUN git clone --depth 1 -b ${FLUX_SCHED_BRANCH} ${FLUX_SCHED_REPO} /opt/flux-sched

# Spack environment written inline (jansson is needed to build the jobtap)
RUN mkdir -p /opt/spack-environment && cat > /opt/spack-environment/spack.yaml <<EOF
spack:
  specs:
    - flux-sched@master
    - flux-core
    - flux-pmix
    - pmix
    - libzmq
    - jansson
  view: /opt/views/view
  concretizer:
    unify: true
  develop:
    flux-sched:
      spec: flux-sched@master
      path: /opt/flux-sched
  packages:
    all:
      require: ["target=:${ARCH}"]
    boost:
      # boost 1.90 + modern cmake break component config lookup (boost_system);
      # pin below it so flux-sched's find_package(Boost) succeeds.
      require: "@1.85.0"
  config:
    install_tree:
      root: /opt/software
EOF

RUN cd /opt/spack-environment && \
    . /opt/spack/share/spack/setup-env.sh && \
    spack env activate . && \
    spack install --fail-fast && spack gc -y

RUN cd /opt/spack-environment && \
    spack env activate --sh -d . > activate.sh && \
    . ./activate.sh && \
    python3 -m ensurepip

# flux-quantum plugins staged into the view.
COPY . /opt/flux-quantum-src
RUN cd /opt/spack-environment && . ./activate.sh && \
    export PKG_CONFIG_PATH=/opt/views/view/lib/pkgconfig:${PKG_CONFIG_PATH} && \
    make -C /opt/flux-quantum-src/flux_quantum/jobtap \
        FLUX_CFLAGS="$(pkg-config --cflags flux-core jansson)" \
        FLUX_LIBS="$(pkg-config --libs flux-core jansson)" \
        CFLAGS="-Wall -fPIC -O2" && \
    mkdir -p /opt/views/view/flux-quantum && \
    cp -R /opt/flux-quantum-src/flux_quantum /opt/views/view/flux-quantum/ && \
    cp -R /opt/flux-quantum-src/cli-plugins  /opt/views/view/flux-quantum/ && \
    install -D /opt/flux-quantum-src/flux_quantum/jobtap/quantum.so \
        /opt/views/view/flux-quantum/jobtap/quantum.so

RUN find -L /opt/views/view/* -type f -exec readlink -f '{}' \; | \
    xargs file -i | grep 'charset=binary' | \
    grep 'x-executable\|x-archive\|x-sharedlib' | \
    awk -F: '{print $1}' | xargs strip || true

# Bare OS image with the view
ARG tag=noble
FROM ubuntu:${tag}
COPY --from=builder /opt/spack-environment /opt/spack-environment
COPY --from=builder /opt/software /opt/software
COPY --from=builder /opt/views /opt/views
RUN { \
      echo '#!/bin/sh' \
      && echo '.' /opt/spack-environment/activate.sh \
      && echo 'exec "$@"'; \
    } > /entrypoint.sh \
&& chmod a+x /entrypoint.sh \
&& ln -s /opt/views/view /opt/view
ENTRYPOINT [ "/entrypoint.sh" ]
CMD [ "/bin/bash" ]
