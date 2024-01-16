1. First, run Pretreatment.py and Pretreatment2.py to obtain specific API information and the API information after maxpooling.
Note:
For APIs with high frequency of occurrence (such as toString444 times, hashCode302 times, equals268 times), the method description for calculating the highest BLEU value is still insufficient. This is because they appear in different packages and classes, undertaking tasks that are generally similar but with completely different details. This results in the BLEU value of their method description often being less than 0.2. To solve this problem, In temp/temp3. csv, we manually corrected the method description of the API with a BLEU value less than 0.5 among the 100 most frequently occurring APIs, making it closer to the description of the function that the method name assumes in most cases. For example, the method description of toString was modified to: The toString() method is used to return a string representation of an object.
2. Put the dataset into raw_ Under the data folder, run s1_ Graphpreprocessor_ AddAPI to obtain the constructed APIMsG graph.
Note: In the code here, an additional node of type has been added to the design of APIMsG, which uses heuristic rules to parse the method names of the API itself. This is a new design we are trying.

3. Place the files in folder code_new2_rule under the APIMsGSum folder src_code/java/graph_data
