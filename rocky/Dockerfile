ARG tag=8
FROM spack/rockylinux${tag}:latest as builder
ARG ARCH=x86_64
ENV ARCH=${ARCH}

RUN dnf update -y && dnf install -y gettext

# Specify flux deps in the spack manifest file (spack.yaml)
RUN mkdir /opt/spack-environment \
&&  (echo spack: \
&&   echo '  specs: [flux-sched, flux-core, libzmq@4.3.4]' \
&&   echo '  view: /opt/views/view' \
&&   echo '  concretizer:' \
&&   echo '    unify: true' \
&&   echo '  packages:' \
&&   echo '    all:' \
&&   echo '      require: ["target=:${ARCH}"]' \
&&   echo '  config:' \
&&   echo '    install_tree: /opt/software') > /opt/spack-environment/spack-template.yaml

RUN envsubst < /opt/spack-environment/spack-template.yaml > /opt/spack-environment/spack.yaml && \
    cat /opt/spack-environment/spack.yaml

# Install the software, remove unnecessary deps
RUN cd /opt/spack-environment && \
    . /opt/spack/share/spack/setup-env.sh && \
    spack env activate . && \
    spack install --fail-fast && spack gc -y

# Strip all the binaries
RUN find -L /opt/views/view/* -type f -exec readlink -f '{}' \; | \
    xargs file -i | \
    grep 'charset=binary' | \
    grep 'x-executable\|x-archive\|x-sharedlib' | \
    awk -F: '{print $1}' | xargs strip

# Modifications to the environment that are necessary to run
RUN cd /opt/spack-environment && \
    spack env activate --sh -d . > activate.sh

# Bare OS image to run the installed executables
ARG tag=8
FROM rockylinux:${tag}

COPY --from=builder /opt/spack-environment /opt/spack-environment
COPY --from=builder /opt/software /opt/software

# paths.view is a symlink, so copy the parent to avoid dereferencing and duplicating it
COPY --from=builder /opt/views /opt/views

RUN { \
      echo '#!/bin/sh' \
      && echo '.' /opt/spack-environment/activate.sh \
      && echo 'exec "$@"'; \
    } > /entrypoint.sh \
&& chmod a+x /entrypoint.sh \
&& ln -s /opt/views/view /opt/view

# Ensure munge is installed and enabled. This is a design flaw
RUN dnf install -y munge && systemctl enable munge

ENTRYPOINT [ "/entrypoint.sh" ]
CMD [ "/bin/bash" ]
