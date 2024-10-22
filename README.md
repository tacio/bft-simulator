# bft-simulator
Byzantine Fault Tolerance Uptime Simulator

Shiny (for python) app that simulates the uptime of a fault tolerant system.  

The time between faults and the duration of a down state are randomly sampled from a Exponential Distribution with $\beta$ (or 1/ $\lambda$ ) scale parameter given as inputs: 
* MTBF (Mean Time Between Failures)
* MTTR (Mean Time to Repair) respectively.


app available at https://fedi.shinyapps.io/bft-simulator1
