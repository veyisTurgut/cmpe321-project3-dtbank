
* We built and tested the application on Mac/Ubuntu.
* We used FastAPI for backend, Vue.js for frontend and PostgreSQL for database. 

## HOW TO RUN
* Create a virtual environment: `virtualenv myenv`
* Activate the virtual environment: `source myenv/bin/activate`
* Install requirements: `pip install -r requirements.txt`
* Set up a postgresql database
* Run database initializer to setup database: `python3 database_initializer.py`
  * We used these credentials for logging in to database, we guess these are the default settings:
  ```python
  {"dbname= dtbank user= postgres host=localhost password=5432 port=5432"}
  ```
* Run the backend application: `uvicorn main:app --reload`
* Open a different terminal and enter frontend folder: `cd frontend`
* Install necessary requirements for frontend: `npm install`
  * If you don't have npm installed, follow this link: [https://www.npmjs.com/get-npm](https://www.npmjs.com/get-npm)
* Run the frontend application: `npm run dev`
* Congrats! Now you can use the application.

* Now, you can access the features of DTBank.


## FEATURES

1. Database managers shall be able to log in to the system with their credentials.
    * Go to http://localhost:3000/ . Below, you see section DBManager Login. Enter database manager username and password.
    * If the username and password is correct, you can use feautes 2-3-4-5 and 6

2. Database managers shall be able to add new users to the system.
    * Login as database manager
    * Go to http://localhost:3000/dbhomecud At left, you see section Add New User. Enter the information of the user you want to add. 

3. Database managers shall be able to update affinity values of drugs using Reaction IDs and delete drugs using DrugBank IDs.
    * Login as database manager
    * To update affinity, go to http://localhost:3000/dbhomecud section Update Affinity. Enter the reaction id and affinity value.
    * To delete a drug, go to http://localhost:3000/dbhomecud section Delete Drug. Enter the drugbank id.

4. Database managers shall be able to delete proteins using UniProt IDs.
    * Login as database manager
    * Go to http://localhost:3000/dbhomecud section Delete Uniprot. Enter the uniprot id.

5. Database managers shall be able to update contributors of papers/documents using Reaction IDs. (Author names, usernames, and passwords will be provided.)
   * Login as database manager
   * Go to http://localhost:3000/dbhomecud section Update Contributors. Enter the reaction id.
   * Then, provide the real names, usernames and passwords of the new contributes into specified boxes, sepatated by commas.
   * If a user does not exist in the database, a new user is created.
   * The contributors are added to the list of contributors of the corresponding article.
   * The institution points are incremented.

6. Database managers shall be able to separately view all drugs listed in DrugBank, all proteins listed in UniProt, all side effects listed in SIDER, all drug - target interactions, all papers and their contributors listed in BindingDB, and all users in DTBank.
   * Login as database manager
   * To view all drugs listed in DrugBank, go to http://localhost:3000/dbhomeget , select route /drugs , click Retrieve.
   * To view all proteins listed in UniProt, go to http://localhost:3000/dbhomeget , select route /prots , click Retrieve.
   * To view all side effects listed in SIDER, go to http://localhost:3000/dbhomeget , select route /siders , click Retrieve.
   * To view all drug - target interactions, go to http://localhost:3000/dbhomeget , select route /drugtargets , click Retrieve.
   * To view all papers and their contributors listed in BindingDB, go to http://localhost:3000/dbhomeget , select route /reactions/articles , click Retrieve.
   * To view all users in DTBank, go to http://localhost:3000/dbhomeget , select route /users , click Retrieve.

7. Users shall be able to log in to the system with their credentials.
    * Login as user
    * Go to http://localhost:3000/ . Above, you see section User Login. Enter username, institution and password.
    * If the username and password is correct, you can use feautes 8-20.

8. Users shall be able to separately view the names, DrugBank IDs, SMILES strings, descriptions, target names, and side effect names of all drugs.
   * Login as user
   * Go to http://localhost:3000/userhome , select route /drugs/plus
   * Click Retrieve 

9. Users shall be able to view all interactions of a specific drug.
   * Login as user
   * Go to http://localhost:3000/userhome , select route /Drugs/{Drug_id}/Interactions
   * Edit the {drug_id} part, enter drugbank id. It does not matter if you delete the curly braces
   * Click Retrieve 

10. Users shall be able to view all side effects of a specific drug.
   * Login as user
   * Go to http://localhost:3000/userhome , select route /Drugs/{Drug_id}/Side_effects
   * Edit the {drug_id} part, enter drugbank id. It does not matter if you delete the curly braces
   * Click Retrieve 
   
11. Users shall be able to view all interacting targets of a specific drug.
   * Login as user
   * Go to http://localhost:3000/userhome , select route /Drugs/{Drug_id}/Targets
   * Edit the {drug_id} part, enter drugbank id. It does not matter if you delete the curly braces
   * Click Retrieve 
 
12. Users shall be able to view interacting drugs of a specific protein.
   * Login as user
   * Go to http://localhost:3000/userhome , select route /prots/{uniprot_id}/drugs
   * Edit the {uniprot_id} part, enter uniprot id. It does not matter if you delete the curly braces
   * Click Retrieve 

13. Users shall be able to view drugs that affect the same protein.
   * Login as user
   * Go to http://localhost:3000/userhome , select route /drugs/same_protein
   * Click Retrieve 

14. Users shall be able to view proteins that bind the same drug.
   * Login as user
   * Go to http://localhost:3000/userhome , select route /prots/same_drugs
   * Click Retrieve 

15. Users shall be able to view drugs that have a specific side effect.
   * Login as user
   * Go to http://localhost:3000/userhome , select route /siders/{umls_cui}/drugs
   * Edit the {umls_cui} part, enter umls cui. It does not matter if you delete the curly braces
   * Click Retrieve 

16. Users shall be able to search a keyword and view the drugs that contain this keyword in their descriptions.
   * Login as user
   * Go to http://localhost:3000/userhome , select route /drugs/keyword/{keyword}
   * Edit the {keyword} part, enter keyword. It does not matter if you delete the curly braces
   * Click Retrieve 

18. Users shall be able to view the drug(s) with the least amount of side effects that interact with a specific protein.
   * Login as user
   * Go to http://localhost:3000/userhome , select route /prots/{uniprot_id}/least_effecting_drug
   * Edit the {uniprot_id} part, enter uniprot id. It does not matter if you delete the curly braces
   * Click Retrieve 

18. Users shall be able to view the DOI of papers and contributors of the corresponding paper.
   * Login as user
   * Go to http://localhost:3000/userhome , select route /articles
   * Click Retrieve 
   
19. Users shall be able to rank institutes according to their total scores (Decreasing order).
   * Login as user
   * Go to http://localhost:3000/userhome , select route /points
   * Click Retrieve 
   
   
20. Users shall be able to filter interacting targets of a specific drug considering the selected measurement type and the range of the affinity values. This must be implemented as a stored procedure. Parameters of this procedure are measurement type, minimum affinity value, and maximum affinity value.
   * Go to http://localhost:3000/userhome
   * select route /drugs/{drug_id}/targets/filter/?measureType={measureType}&min_affinity={min_affinity}&max_affinity={max_affinity}
   * Edit the {drug_id} part, enter drugbank id. It does not matter if you delete the curly braces
   * Edit the {measureType} part, enter measurement type. It does not matter if you delete the curly braces
   * Edit the {min_affinity} part, enter minimum affinity value. It does not matter if you delete the curly braces
   * Edit the {max_affinity} part, enter maximum affinity value. It does not matter if you delete the curly braces
   * Click Retrieve 

   * See function filter_targets


21. The system shall have three triggers:
(a) When a drug is deleted, it should be removed from the the list of the interacting drugs of other drugs,
and its corresponding entries from SIDER and BindingDB.
   * See trigger delete_drug_related_rows which executes procedure delete_rows_with_drugbank_id
   * See trigger delete_drug_related_reaction which executes procedure delete_reaction_by_drug

(b) When a protein is deleted, its corresponding entries from BindingDB should be removed.
   * See trigger delete_protein_related_rows which executes procedure delete_rows_with_uniprot_id
   * See trigger delete_protein_related_reaction which executes procedure delete_reaction_by_protein

(c) When a new publication is added to the system, the corresponding institute gets 5 points for a new publication and gets 2 points for each individual who contributed to it. Also, when there is an update on the publication that changes the number of contributors, update the corresponding institute’s score accordingly.
   * See trigger insert_institutions which executes procedure insert_institutions
   * See trigger article_points which executes procedure increase_institution_points
