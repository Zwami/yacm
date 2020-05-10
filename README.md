# yacm
Yet Another Covid Model

Execute using python3 run.py
Most configuration options are exposed in web interface, but certain parameters are only accessible within server.py. Notably these include 
* The transition probabilities for the movement of symptomatic agents.
* The transition probbabilities for the progression of the disease within an agent after they are initially infected. 

The reason that these options are not exposed in the same manner is due to some complexity in how to configure the the progression rates, namely in that not all of the states are recurrent in these cases.


*** KNOWN ISSUES ***
The X axis on the mesa charts is relative to the current "step" and is based on an internal clock of the server vs the received "step" data from the model. A result of this is that setting the step rate too high will cause the model to appear to be progressing faster than the data is actually supporting, and can mess up the apparent time of the scenario. 
