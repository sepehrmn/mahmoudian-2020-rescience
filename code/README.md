# mahmoudian-2020-rescience
Sepehr Mahmoudian's reproduction of Smyth, Phillips, Kay 1996

This repository contains a successful replication of the Smyth paper for the ReScience C journal. 

---

There are no special dependencies or computing resources required to run the code.

Tested with:
```
Python 3.8.1
numpy 1.18
scipy 1.4  
matplotlib 3.1.3
```
To install the requirements above one could simply use ```pip install -r requirements.txt``` after getting the correct python version.

---

It's simple to run the code:
```
python main.py
```

The three figures will be displayed in a sequence.

---


The fastest way to test your activation function would be to replace one of the four activation functions in main.py. Probably that would be the 4th activation function (no context) and then renaming it in functions_X__R_C dictionary. To have all four and your activation function, first adjust the n_functions in params.py then put it in the main loop where result of the activation functions are calculated and finally add it to the functions_X__R_C dictionary.
