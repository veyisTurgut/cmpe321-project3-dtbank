from typing import List
import psycopg2
import hashlib as hasher
from starlette.responses import Response
from datetime import datetime, timedelta
import schemas
import mappers
from fastapi.middleware.cors import CORSMiddleware
from fastapi import FastAPI, HTTPException

app = FastAPI()

origins = ["*"]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


##############---- HELPERS START -----###########################
current_session_credentials = {
    "username": "",
    "institution": "",
    "logintime": ""
}


def update_current_session_credentials(username, institution=""):
    current_session_credentials["username"] = username
    current_session_credentials["institution"] = institution
    current_session_credentials["logintime"] = datetime.now().strftime("%H:%M:%S")


def is_session_valid_user():
    # ensure that user logged in 30 mins before
    if current_session_credentials["logintime"] == '':
        return False
    time_difference = datetime.strptime(datetime.now().strftime(
        "%H:%M:%S"), "%H:%M:%S") - datetime.strptime(current_session_credentials["logintime"], "%H:%M:%S")
    return (not time_difference > timedelta(minutes=30)) and current_session_credentials["institution"] != ""


def is_session_valid_db():
    # ensure that user logged in 30 mins before
    if current_session_credentials["logintime"] == '':
        return False
    time_difference = datetime.strptime(datetime.now().strftime(
        "%H:%M:%S"), "%H:%M:%S") - datetime.strptime(current_session_credentials["logintime"], "%H:%M:%S")
    return (not time_difference > timedelta(minutes=30)) and current_session_credentials["institution"] == ""


def hash_password(pwd: str):
    password_hasher = hasher.sha256()
    password_hasher.update(pwd.encode("utf-8"))
    hashed_password = password_hasher.hexdigest()
    return hashed_password


############------ HELPERS END -------########################

@app.get("/")
async def home():
    return "there is nothing here"

########### -----DB MANAGER OPERATIONS START ----- ###########


# 1 Database managers shall be able to log in to the system with their credentials.

@app.post("/database_managers/login",
          response_model=str)
async def login(credentials: schemas.DMLoginCredentials):
    con = psycopg2.connect("dbname= dtbank user= postgres host=localhost password=5432 port=5432")
    cur = con.cursor()

    # check if a db manager with that username exists
    cur.execute('''SELECT * FROM databasemanager WHERE username = %s''', [credentials.username])
    data = cur.fetchone()
    if data is None:
        return Response("DB Manager not found!", status_code=404)
    # check if the hashed password matches the one in db
    hashed_password = hash_password(credentials.password)
    if not data[1] == hashed_password:
        return Response("Password invalid!", status_code=400)
    # if the password matches, update credentials, return successful response
    update_current_session_credentials(credentials.username)

    con.commit()
    con.close()
    return "OK"


# todo bence burda user response dondurmeliyiz
# 2 Database managers shall be able to add new users to the system.
@app.post("/users",
          response_model=str)
async def add_user(user: schemas.CreateUser):
    if not is_session_valid_db():
        raise HTTPException(status_code=403, detail="First login!")
    con = psycopg2.connect("dbname= dtbank user= postgres host=localhost password=5432 port=5432")
    cur = con.cursor()

    # try to insert into database, if error occurs, catch
    hashed_password = hash_password(user.password)
    try:
        cur.execute('''INSERT INTO Users(realname, username, password, institution) VALUES (%s,%s,%s,%s)''',
                    [user.realname, user.username, hashed_password, user.institution])
    except Exception as err:
        raise HTTPException(status_code=403, detail="A user with the same username and institution exists")

    con.commit()
    con.close()
    return "OK"


# 3a Database managers shall be able to update affinity values of drugs using Reaction IDs
@app.put("/reactions/{reaction_id}/affinity",
         response_model=mappers.ReactionResponse)
async def update_affinity(reaction_id: str, affinity: float):
    if not is_session_valid_db():
        raise HTTPException(status_code=403, detail="First login!")
    con = psycopg2.connect("dbname= dtbank user= postgres host=localhost password=5432 port=5432")
    cur = con.cursor()

    if not reaction_id.isdigit():
        raise HTTPException(status_code=422, detail="Reaction id should be integer")

    # check if that reaction exists in the database, if not, return error
    cur.execute('''SELECT * FROM BindingDB WHERE reaction_id = %s''', [reaction_id])
    data = cur.fetchone()
    if data is None:
        raise HTTPException(status_code=404, detail="Reaction not found")
    # if reaction is found, it's affinity value can be updated
    cur.execute('''UPDATE BindingDB SET affinity = %s  WHERE reaction_id = %s ''', [affinity, reaction_id])

    con.commit()
    con.close()
    return schemas.ReactionResponse(items=[mappers.reaction_mapper(data)])


# 3b Database managers shall be able to delete drugs using DrugBank IDs.
@app.delete("/drugs/{drug_id}",
            response_model=None)
async def delete_drug(drug_id: str):
    if not is_session_valid_db():
        raise HTTPException(status_code=403, detail="First login!")
    con = psycopg2.connect("dbname= dtbank user= postgres host=localhost password=5432 port=5432")
    cur = con.cursor()

    # check if that drug exists in the database, if not, return error
    cur.execute('''SELECT * FROM Drugbank WHERE drugbank_id = %s''', [drug_id])
    data = cur.fetchone()
    if data is None:
        raise HTTPException(status_code=404, detail="Drug not found")
    # if the drug exists, it can be deleted
    cur.execute('''DELETE FROM Drugbank WHERE drugbank_id = %s''', [drug_id])

    con.commit()
    con.close()
    return None


# 4 Database managers shall be able delete proteins using Uniprot IDs.
@app.delete("/prots/{uniprot_id}",
            response_model=None)
async def delete_prot(uniprot_id: str):
    if not is_session_valid_db():
        raise HTTPException(status_code=403, detail="First login!")
    con = psycopg2.connect("dbname= dtbank user= postgres host=localhost password=5432 port=5432")
    cur = con.cursor()

    # check if that drug exists in the database, if not, return error
    cur.execute('''SELECT * FROM Uniprot WHERE uniprot_id = %s''', [uniprot_id])
    data = cur.fetchone()
    if data is None:
        raise HTTPException(status_code=404, detail="Protein not found")
    # if the drug exists, it can be deleted
    cur.execute('''DELETE FROM Uniprot WHERE uniprot_id = %s''', [uniprot_id])

    con.commit()
    con.close()
    return None


# 5 Database managers shall be able to update contributors of papers/documents using Reaction IDs.
# (Author names, usernames, and passwords will be provided.)
@app.put("/articles/{reaction_id}",
         response_model=None)
async def update_contributors_of_articles(reaction_id: int, contributors: List[schemas.Author]):
    if not is_session_valid_db():
        raise HTTPException(status_code=403, detail="First login!")
    con = psycopg2.connect("dbname= dtbank user= postgres host=localhost password=5432 port=5432")
    cur = con.cursor()

    # get the article doi and institution the reaction is related to, if not found, return error
    cur.execute(''' SELECT institution, doi FROM Users, 
                        (SELECT author_id, ArticleAuthor.article_doi as doi FROM ArticleAuthor, 
                            (SELECT article_doi FROM BindingDB WHERE reaction_id = %s) DB
                        WHERE ArticleAuthor.article_doi = DB.article_doi) AD
                    WHERE AD.author_id = Users.user_id''', [reaction_id])
    data = cur.fetchone()
    if data is None:
        raise HTTPException(status_code=404, detail="Reaction not found")

    institution, article_doi = data[0], data[1]
    # for each contributor, check if they are registered as users. if not, register them
    for contributor in contributors:
        cur.execute('''SELECT * FROM users WHERE realname = %s''',
                    [contributor.realname])
        data = cur.fetchone()
        if data is None:
            hashed_password = hash_password(contributor.password)
            try:
                cur.execute('''INSERT INTO Users(realname, username, password, institution) VALUES (%s,%s,%s,%s)''',
                            [contributor.realname, contributor.username, hashed_password, institution])
            except Exception as err:
                raise HTTPException(status_code=403, detail="A user with the same username and institution exists")

    # after making sure each contributor is registered to the system, insert pairs into articleauthor
    for contributor in contributors:
        cur.execute('''SELECT * FROM users WHERE realname = %s''', [contributor.realname])
        data = cur.fetchone()
        user_id = data[0]
        cur.execute('''INSERT INTO ArticleAuthor(author_id, article_doi) VALUES (%s,%s)''', [user_id, article_doi])

    con.commit()
    con.close()
    return None


# 6a Database managers shall be able to view all drugs listed in DrugBank,
@app.get("/drugs",
         response_model=schemas.DrugSiderResponse)
async def get_drugs():
    if not is_session_valid_db():
        raise HTTPException(status_code=403, detail="First login!")
    con = psycopg2.connect("dbname= dtbank user= postgres host=localhost password=5432 port=5432")
    cur = con.cursor()

    cur.execute('''SELECT * FROM Drugbank''')
    data = cur.fetchall()

    con.commit()
    con.close()
    return schemas.DrugSiderResponse(items=[mappers.drug_sider_mapper(s) for s in data])


# 6b Database managers shall be able to view all proteins listed in UniProt
@app.get("/prots",
         response_model=schemas.UniprotResponse)
async def get_proteins():
    if not is_session_valid_db():
        raise HTTPException(status_code=403, detail="First login!")
    con = psycopg2.connect("dbname= dtbank user= postgres host=localhost password=5432 port=5432")
    cur = con.cursor()

    cur.execute('''SELECT * FROM Uniprot''')
    data = cur.fetchall()

    con.commit()
    con.close()
    return schemas.UniprotResponse(items=[mappers.uniprot_mapper(s) for s in data])


# 6c Database managers shall be able to view all side effects listed in SIDER
@app.get("/siders",
         response_model=schemas.SiderResponse)
async def get_siders():
    if not is_session_valid_db():
        raise HTTPException(status_code=403, detail="First login!")
    con = psycopg2.connect("dbname= dtbank user= postgres host=localhost password=5432 port=5432")
    cur = con.cursor()

    cur.execute('''SELECT * FROM Sider''')
    data = cur.fetchall()

    con.commit()
    con.close()
    return schemas.SiderResponse(items=[mappers.sider_mapper(s) for s in data])


# 6d Database managers shall be able to view all drug - target interactions (listed in BindingDB?)
@app.get("/drugtargets",
         response_model=schemas.DrugTargetResponse)
async def get_drug_target_interactions():
    if not is_session_valid_db():
        raise HTTPException(status_code=403, detail="First login!")
    con = psycopg2.connect("dbname= dtbank user= postgres host=localhost password=5432 port=5432")
    cur = con.cursor()

    # From ReactingDrug and ReactingProt, match the pairs with same reaction id
    cur.execute('''SELECT d.drugbank_id, r.uniprot_id FROM reactingdrug d
                    LEFT JOIN reactingprot r
                    ON d.reaction_id = r.reaction_id''')
    data = cur.fetchall()

    con.commit()
    con.close()
    return schemas.DrugTargetResponse(items=[mappers.drugtarget_mapper(s) for s in data])


# 6e Database managers shall be able to view all papers and their contributors listed in BindingDB
@app.get("/reactions/articles",
         response_model=schemas.ArticleResponse)
async def get_articles_in_binding_db():
    if not is_session_valid_db():
        raise HTTPException(status_code=403, detail="First login!")
    con = psycopg2.connect("dbname= dtbank user= postgres host=localhost password=5432 port=5432")
    cur = con.cursor()

    # get article - author pairs
    cur.execute('''SELECT R.realname, R.article_doi FROM
                    (SELECT * FROM ArticleAuthor A
                    LEFT JOIN Users U on U.user_id = A.author_id) R''')
    data = cur.fetchall()

    # group the response using doi as key
    grouped = {}
    for s in data:
        grouped.setdefault(s[1], []).append(s[0])
    response_list = [(k, v) for k, v in grouped.items()]

    con.commit()
    con.close()
    return schemas.ArticleResponse(items=[mappers.article_mapper(s) for s in response_list])


# 6f Database managers shall be able to view all users in DTBank.
@app.get("/users",
         response_model=schemas.UserConfidentialResponse)
async def get_users():
    if not is_session_valid_db():
        raise HTTPException(status_code=403, detail="First login!")
    con = psycopg2.connect("dbname= dtbank user= postgres host=localhost password=5432 port=5432")
    cur = con.cursor()

    cur.execute('''SELECT username, institution,realname FROM Users''')
    data = cur.fetchall()

    con.commit()
    con.close()
    return schemas.UserConfidentialResponse(items=[mappers.user_confidential_mapper(u) for u in data])


############ ----- DB MANAGER OPERATIONS END ----- ############

############ ----- USER OPERATIONS START ----- ############

# 7 Users shall be able to log in to the system with their credentials.
@app.post("/users/login",
          response_model=str)
async def login(credentials: schemas.UserLoginCredentials):
    con = psycopg2.connect("dbname= dtbank user= postgres host=localhost password=5432 port=5432")
    cur = con.cursor()
    # check if a user with that username and institution exists
    cur.execute('''SELECT * FROM users WHERE username = %s AND institution = %s''',
                [credentials.username, credentials.institution])
    data = cur.fetchone()
    if data is None:
        return Response("User not found!", status_code=404)

    # check if the hashed password matches the one in db
    hashed_password = hash_password(credentials.password)
    if not data[3] == hashed_password:
        return Response("Password invalid!", status_code=400)
    # if the password matches, update credentials, return successful response
    update_current_session_credentials(credentials.username, credentials.institution)

    con.commit()
    con.close()
    return "OK"


# 8 Users shall be able to separately view the names, DrugBank IDs, SMILES strings, descriptions, target names,
# and side effect names of all drugs
@app.get("/drugs/plus",
         response_model=schemas.DrugSiderResponse)
async def get_drugsider():
    if not is_session_valid_user():
        raise HTTPException(status_code=403, detail="First login!")
    con = psycopg2.connect("dbname= dtbank user= postgres host=localhost password=5432 port=5432")

    cur = con.cursor()
    cur.execute('''SELECT * FROM Drugbank''')
    data = cur.fetchall()
    for i in range(len(data)):
        drug_id = data[i][0]
        # get uniprot names
        SQL_script = '''SELECT protein_name FROM Uniprot,  
            (SELECT uniprot_id FROM ReactingDrug INNER JOIN ReactingProt ON ReactingProt.reaction_id = ReactingDrug.reaction_id  WHERE ReactingDrug.drugbank_id = %s) U
            WHERE U.uniprot_id = Uniprot.uniprot_id;'''
        cur.execute(SQL_script, (drug_id,))  # Note: no % operator
        target_names = cur.fetchall()
        data[i] = (*data[i], target_names)
        # get side effect names
        SQL_script = ''' SELECT side_effect_name FROM  Sider, DrugSider
        WHERE Sider.umls_cui = Drugsider.umls_cui AND DrugSider.drugbank_id = %s;'''
        cur.execute(SQL_script, (drug_id,))  # Note: no % operator
        side_effect_names = cur.fetchall()
        data[i] = (*data[i], side_effect_names)

    con.commit()
    con.close()
    return schemas.DrugSiderResponse(items=[mappers.drug_sider_mapper(s) for s in data])


# 9 Users shall be able to view all interactions of a specific drug.
@app.get("/drugs/{drug_id}/interactions",
         response_model=schemas.InteractingDrugListResponse)
async def get_drug_interactions(drug_id: str):
    if not is_session_valid_user():
        raise HTTPException(status_code=403, detail="First login!")
    con = psycopg2.connect("dbname= dtbank user= postgres host=localhost password=5432 port=5432")
    cur = con.cursor()

    # check if that drug exists in the database, if not, return error
    cur.execute('''SELECT * FROM Drugbank WHERE drugbank_id = %s''', [drug_id])
    data = cur.fetchone()
    if data is None:
        raise HTTPException(status_code=404, detail="Drug not found")

    # if the drug exists, find the names and drugbank_ids of the drugs it interacts with, using InteractingDrugs
    cur.execute(''' SELECT drugbank_id, drug_name FROM 
                    (SELECT drug2 FROM InteractingDrugs WHERE drug1 = %s) D, Drugbank 
                    WHERE drug2=drugbank_id''',
                [drug_id])
    data = cur.fetchall()

    con.commit()
    con.close()
    return schemas.InteractingDrugListResponse(items=[mappers.interacting_drug_mapper(d) for d in data])


# 10 Users shall be able to view all side effects of a specific drug.
@app.get("/drugs/{drug_id}/side_effects",
         response_model=schemas.SiderResponse)
async def get_drug_side_effects(drug_id: str):
    if not is_session_valid_user():
        raise HTTPException(status_code=403, detail="First login!")
    con = psycopg2.connect("dbname= dtbank user= postgres host=localhost password=5432 port=5432")
    cur = con.cursor()

    # check if that drug exists in the database, if not, return error
    cur.execute('''SELECT * FROM Drugbank WHERE drugbank_id = %s''', [drug_id])
    data = cur.fetchone()
    if data is None:
        raise HTTPException(status_code=404, detail="Drug not found")

    # if the drug exits, get the umls_cui and side effect names of the drug using DrugSider
    cur.execute(''' SELECT Sider.umls_cui, Sider.side_effect_name FROM 
                        (SELECT * FROM DrugSider WHERE drugbank_id = %s) SN 
                        INNER JOIN Sider ON SN.umls_cui = Sider.umls_cui ''',
                [drug_id])
    data = cur.fetchall()

    con.commit()
    con.close()
    return schemas.SiderResponse(items=[mappers.sider_mapper(s) for s in data])


# 11 Users shall be able to view all interacting targets of a specific drug.
@app.get("/drugs/{drug_id}/targets",
         response_model=schemas.UniprotResponse)
async def get_drug_targets(drug_id: str):
    if not is_session_valid_user():
        raise HTTPException(status_code=403, detail="First login!")
    con = psycopg2.connect("dbname= dtbank user= postgres host=localhost password=5432 port=5432")
    cur = con.cursor()

    # check if that drug exists in the database, if not, return error
    cur.execute('''SELECT * FROM Drugbank WHERE drugbank_id = %s''', [drug_id])
    data = cur.fetchone()
    if data is None:
        raise HTTPException(status_code=404, detail="Drug not found")

    # if the drug exists, get the interacting targets using ReactingDrug and ReactingProt
    cur.execute(''' SELECT Uniprot.* FROM 
                    (SELECT ReactingProt.uniprot_id as uniprot_idd FROM 
                        (SELECT reaction_id FROM ReactingDrug WHERE drugbank_id = %s) R
                        INNER JOIN ReactingProt ON R.reaction_id = ReactingProt.reaction_id) U
                    INNER JOIN Uniprot ON Uniprot.uniprot_id = U.uniprot_idd ''',
                [drug_id])
    data = cur.fetchall()

    con.commit()
    con.close()
    return schemas.UniprotResponse(items=[mappers.uniprot_mapper(s) for s in data])


# 12 Users shall be able to view interacting drugs of a specific protein.
@app.get("/prots/{uniprot_id}/drugs",
         response_model=schemas.DrugResponse)
async def get_protein_drugs(uniprot_id: str):
    if not is_session_valid_user():
        raise HTTPException(status_code=403, detail="First login!")
    con = psycopg2.connect("dbname= dtbank user= postgres host=localhost password=5432 port=5432")
    cur = con.cursor()

    # check if that protein exists in the database, if not, return error
    cur.execute('''SELECT * FROM Uniprot WHERE uniprot_id = %s''', [uniprot_id])
    data = cur.fetchone()
    if data is None:
        raise HTTPException(status_code=404, detail="Protein not found")

    # if the protein exists, get the drugs it insteracs with using ReactingProt and ReactingDrug
    cur.execute(''' SELECT DrugBank.drugbank_id,DrugBank.drug_name,DrugBank.smiles ,DrugBank.description FROM 
                    (SELECT drugbank_id FROM 
                        (SELECT reaction_id FROM ReactingProt WHERE uniprot_id = %s) R, ReactingDrug 
                        WHERE R.reaction_id = ReactingDrug.reaction_id
                        ) D, 
                    DrugBank WHERE D.drugbank_id = DrugBank.drugbank_id''',
                [uniprot_id])
    data = cur.fetchall()

    con.commit()
    con.close()
    return schemas.DrugResponse(items=[mappers.drug_mapper(s) for s in list(set(data))])


# 13 Users shall be able to view drugs that affect the same protein.
@app.get("/drugs/same_protein",
         response_model=dict)
async def get_drugs_with_same_protein():
    if not is_session_valid_user():
        raise HTTPException(status_code=403, detail="First login!")
    con = psycopg2.connect("dbname= dtbank user= postgres host=localhost password=5432 port=5432")
    cur = con.cursor()

    cur.execute("SELECT * FROM Uniprot")
    proteins = cur.fetchall()
    response = []
    for protein in proteins:
        cur.execute('''SELECT DrugBank.drugbank_id,DrugBank.drug_name,DrugBank.description 
        FROM (select drugbank_id FROM (select reaction_id FROM ReactingProt WHERE uniprot_id =%s) R, ReactingDrug 
        WHERE R.reaction_id = ReactingDrug.reaction_id) D, DrugBank WHERE D.drugbank_id = DrugBank.drugbank_id''',
                    [protein[0]])
        data = cur.fetchall()
        drug_list = []
        for drug in data:
            drug_list.append(drug[0])
        response.append({
            "uniprot_id": protein[0],
            "drugs": drug_list
        })

    con.commit()
    con.close()
    return {"items": [{"uniprot_id": s["uniprot_id"], "drugbank_ids": list(set(s["drugs"]))} for s in response]}


# 14 Users shall be able to view proteins that bind the same drug.
@app.get("/prots/same_drugs",
         response_model=dict)
async def get_proteins_with_same_drug():
    if not is_session_valid_user():
        raise HTTPException(status_code=403, detail="First login!")
    con = psycopg2.connect("dbname= dtbank user= postgres host=localhost password=5432 port=5432")
    cur = con.cursor()

    cur.execute("SELECT * FROM Drugbank")
    drugs = cur.fetchall()
    response = []
    for drug in drugs:
        cur.execute('''SELECT Uniprot.uniprot_id
        FROM (SELECT uniprot_id from (SELECT reaction_id FROM ReactingDrug WHERE drugbank_id =%s) R, ReactingProt 
        WHERE R.reaction_id = ReactingProt.reaction_id) P, Uniprot WHERE P.uniprot_id = Uniprot.uniprot_id''',
                    [drug[0]])
        data = cur.fetchall()
        protein_list = []
        for protein in data:
            protein_list.append(protein[0])
        response.append({
            "prots": protein_list,
            "drugbank_id": drug[0]
        })

    con.commit()
    con.close()
    return {"items": [{"drugbank_id": s["drugbank_id"], "uniprot_ids": list(set(s["prots"]))} for s in response]}


# 15 Users shall be able to view drugs that have a specific side effect.
@app.get("/siders/{umls_cui}/drugs",
         response_model=schemas.DrugResponse)
async def get_drugs_with_side_effect(umls_cui: str):
    if not is_session_valid_user():
        raise HTTPException(status_code=403, detail="First login!")
    con = psycopg2.connect("dbname= dtbank user= postgres host=localhost password=5432 port=5432")
    cur = con.cursor()

    # check if that side effect exists in the database, if not, return error
    cur.execute('''SELECT * FROM Sider WHERE Sider.umls_cui = %s''', [umls_cui])
    data = cur.fetchone()
    if data is None:
        raise HTTPException(status_code=404, detail="Sider not found")

    # if the side effect exists, get the drugs its related with using drugsider
    cur.execute(''' SELECT Drugbank.drugbank_id, Drugbank.drug_name,Drugbank.smiles, Drugbank.description FROM
                        (SELECT drugbank_id FROM DrugSider WHERE umls_cui = %s) DS
                        INNER JOIN Drugbank ON DS.drugbank_id = Drugbank.drugbank_id''', [umls_cui])
    data = cur.fetchall()

    con.commit()
    con.close()
    return schemas.DrugResponse(items=[mappers.drug_mapper(s) for s in data])


# 16 Users shall be able to search a keyword and view the drugs that contain this keyword in their descriptions.
@app.get("/drugs/keyword/{keyword}",
         response_model=schemas.DrugResponse)
async def get_drug_keyword(keyword: str):
    if not is_session_valid_user():
        raise HTTPException(status_code=403, detail="First login!")
    con = psycopg2.connect("dbname= dtbank user= postgres host=localhost password=5432 port=5432")
    cur = con.cursor()

    cur.execute('''SELECT drugbank_id, drug_name, smiles,description FROM DrugBank WHERE description LIKE %s ''',
                ["%" + keyword + "%"])
    data = cur.fetchall()
    response = []

    con.commit()
    con.close()
    return schemas.DrugResponse(items=[mappers.drug_mapper(s) for s in data])


# 17 Users shall be able to view the drug(s)
# with the least amount of side effects that interact with a specific protein.
@app.get("/prots/{uniprot_id}/least_effecting_drug",
         response_model=schemas.DrugSideNumberResponse)
async def least_effecing_drug_of_a_prot(uniprot_id: str):
    if not is_session_valid_user():
        raise HTTPException(status_code=403, detail="First login!")
    con = psycopg2.connect("dbname= dtbank user= postgres host=localhost password=5432 port=5432")
    cur = con.cursor()

    cur.execute('''SELECT DL.drugbank_id, DrugBank.drug_name, DrugBank.smiles, DrugBank.description, DL.cnt 
                FROM  (WITH my_query AS
                        (SELECT DrugSider.drugbank_id, COUNT(DrugSider.drugbank_id) AS cnt FROM
                            (SELECT drugbank_id FROM ReactingProt, ReactingDrug
                            WHERE  ReactingDrug.reaction_id = ReactingProt.reaction_id
                            AND ReactingProt.uniprot_id = %s) D, DrugSider
                            WHERE D.drugbank_id = DrugSider.drugbank_id
                            GROUP BY DrugSider.drugbank_id
                        ORDER BY cnt)
                SELECT * from my_query
                WHERE cnt in (SELECT min(cnt) FROM my_query)) DL, DrugBank 
                WHERE DrugBank.drugbank_id = DL.drugbank_id;''',
                [uniprot_id])
    data = cur.fetchall()

    con.commit()
    con.close()
    return schemas.DrugSideNumberResponse(items=[mappers.drug_point_mapper(s) for s in data])


# 18 Users shall be able to view the DOI of papers and contributors.
@app.get("/articles",
         response_model=schemas.ArticleResponse)
async def get_doi_and_authors_of_articles():
    if not is_session_valid_user():
        raise HTTPException(status_code=403, detail="First login!")
    con = psycopg2.connect("dbname= dtbank user= postgres host=localhost password=5432 port=5432")
    cur = con.cursor()

    # get article-author pairs
    cur.execute(''' SELECT Users.realname, A.article_doi FROM 
                        (SELECT author_id, article_doi FROM ArticleAuthor) A, Users 
                        WHERE Users.user_id = A.author_id;''')
    data = cur.fetchall()

    # group the response using doi as key
    grouped = {}
    for s in data:
        grouped.setdefault(s[1], []).append(s[0])
    response_list = [(k, v) for k, v in grouped.items()]

    con.commit()
    con.close()
    return schemas.ArticleResponse(items=[mappers.article_mapper(s) for s in response_list])


# 19 Users shall be able to rank institutes according to their total scores (Decreasing order).

@app.get("/points",
         response_model=schemas.InstitutionPointResponse)
async def get_points_of_institutions():
    if not is_session_valid_user():
        raise HTTPException(status_code=403, detail="First login!")
    con = psycopg2.connect("dbname= dtbank user= postgres host=localhost password=5432 port=5432")
    cur = con.cursor()

    # institutions and their points are stored in InstitutionPoints, order by descending order of scores
    cur.execute(''' SELECT * FROM InstitutionPoints ORDER BY points DESC;''')
    data = cur.fetchall()

    con.commit()
    con.close()
    return schemas.InstitutionPointResponse(items=[mappers.institution_point_mapper(s) for s in data])

# 20 Users shall be able to filter interacting targets of a specific drug considering the selected measurement
#    type and the range of the affinity values. This must be implemented as a stored procedure. Parameters
#    of this procedure are measurement type, minimum affinity value, and maximum affinity value.
#
@app.get("/drugs/{drug_id}/targets/filter/", response_model=schemas.UniprotResponse)
async def get_targets_of_drugs(drug_id:str,measureType: str, min_affinity: float, max_affinity: float):
    if not is_session_valid_user():
        raise HTTPException(status_code=403, detail="First login!")
    con = psycopg2.connect(
        "dbname= dtbank user= postgres host=localhost password=5432 port=5432")
    cur = con.cursor()
    cur.execute(f"Select * FROM filter_targets('{drug_id}','{measureType}',{min_affinity},{max_affinity});")
    data = cur.fetchall()
    return schemas.UniprotResponse(items = [mappers.uniprot_mapper(s) for s in data])

############ -----USER OPERATIONS END ----- ############
