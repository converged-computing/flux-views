# Spack Flux View Containers

This is an experiment to build Flux entirely into isolated spack views, and with the goal
of refactoring the Flux Operator so that application logic is separate from Flux.
This has proven to work with the Metrics Operator and I'm hoping is a good solution here.
It works as follows:

1. We build an isolated view with Flux
2. We add it to a job as a sidecar container
3. We do Flux setup within this container
4. We move the entire thing to a shared empty volume with the other application container
5. The application container entrypoitn is edited to get wrapped with Flux

We will see if it works! 
