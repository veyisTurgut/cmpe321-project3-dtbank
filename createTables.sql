-- DatabaseManager(username: string, password: string)
CREATE TABLE IF NOT EXISTS DatabaseManager (
    username        TEXT NOT NULL,
    password        TEXT NOT NULL,
    PRIMARY KEY (username)
);


-- User(user_id: int, username: string, password: string, institution: string)
CREATE TABLE IF NOT EXISTS Users (
	user_id			SERIAL,
    realname        TEXT NOT NULL,
    username		TEXT NOT NULL,
	password		TEXT NOT NULL,
	institution		TEXT NOT NULL,
	PRIMARY KEY(user_id),
    UNIQUE (username,institution)
);

-- Sider(umls_cui: string, side_effect_name: string)
CREATE TABLE IF NOT EXISTS Sider (
	umls_cui		    	TEXT NOT NULL,
	side_effect_name		TEXT NOT NULL,
	PRIMARY KEY(umls_cui)
);

-- Uniprot(uniprot_id: string, sequence: string)
CREATE TABLE IF NOT EXISTS Uniprot (
	uniprot_id		TEXT NOT NULL,
	protein_name    TEXT NOT NULL,
	sequence		TEXT NOT NULL,
	PRIMARY KEY(uniprot_id)
);

-- DrugBank(drugbank_id: string, drug_name: string, description: string, smiles: string)
CREATE TABLE IF NOT EXISTS DrugBank (
	drugbank_id		TEXT NOT NULL,
	drug_name		TEXT NOT NULL,
	smiles		    TEXT NOT NULL,
	description		TEXT NOT NULL,
	PRIMARY KEY(drugbank_id)
);

-- Article(doi:string, authors: string, first_author_id: int)
CREATE TABLE IF NOT EXISTS Article (
	doi			        TEXT NOT NULL,
	PRIMARY KEY(doi)
);

CREATE TABLE IF NOT EXISTS InstitutionPoints (
	institution		TEXT NOT NULL,
	points          INTEGER NOT NULL,
	PRIMARY KEY(institution)
);


CREATE TABLE IF NOT EXISTS ArticleAuthor (
	author_article_id       SERIAL,
    author_id               INTEGER NOT NULL,
    article_doi             TEXT NOT NULL,
	PRIMARY KEY(author_article_id),
    UNIQUE(author_id,article_doi),   -- restrict the same tuple to be added multiple times
    FOREIGN KEY(article_doi) REFERENCES Article(doi), -- on delete vsvs
    FOREIGN KEY(author_id) REFERENCES Users(user_id)    -- on delete update vsvs
);


CREATE TABLE IF NOT EXISTS BindingDB (
	reaction_id		INTEGER NOT NULL,
	measure		    TEXT NOT NULL,
	affinity		REAL NOT NULL,
	article_doi		TEXT NOT NULL,
	PRIMARY KEY(reaction_id),
	FOREIGN KEY(article_doi) REFERENCES Article(doi)
        ON UPDATE CASCADE   -- if an article's doi changes, change it here also
        ON DELETE RESTRICT  -- do not allow a reaction's article to be removed
);

CREATE TABLE IF NOT EXISTS InteractingDrugs (
	interacting_drug_id 	SERIAL,
	drug1			        TEXT NOT NULL,
	drug2			        TEXT NOT NULL,
	PRIMARY KEY(interacting_drug_id),
	UNIQUE (drug1,drug2),   -- restrict the same reaction to be added multiple times
  	FOREIGN KEY(drug1) REFERENCES DrugBank(drugbank_id)
  	    ON UPDATE CASCADE
  	    ON DELETE CASCADE,
  	FOREIGN KEY(drug2) REFERENCES DrugBank(drugbank_id)
        ON UPDATE CASCADE
        ON DELETE CASCADE
        -- if there is a change on one of the interacting drugs, change it here also
        -- When a drug is deleted, it should be removed from the the list of the interacting drugs of other drugs
);

CREATE TABLE IF NOT EXISTS ReactingProt (
    reacting_prot_id        	SERIAL,
    reaction_id             	INTEGER NOT NULL,
    uniprot_id              	TEXT NOT NULL,
    PRIMARY KEY (reacting_prot_id),
    UNIQUE (reaction_id,uniprot_id),   -- restrict the same tuple to be added multiple times
    FOREIGN KEY (reaction_id) REFERENCES BindingDB(reaction_id)
        ON UPDATE CASCADE   -- if a reaction is updated, change it here also
  	    ON DELETE CASCADE,  -- if a reaction is deleted, delete the reaction-protein pair
    FOREIGN KEY (uniprot_id) REFERENCES Uniprot(uniprot_id)
        ON UPDATE CASCADE   -- if a protein is updated, change it here also
  	    ON DELETE CASCADE   -- When a protein is deleted, its corresponding entries from BindingDB should be removed.
);

CREATE TABLE IF NOT EXISTS ReactingDrug (
    reacting_drug_id        SERIAL,
    drugbank_id             TEXT NOT NULL,
    reaction_id           	INTEGER NOT NULL,
    PRIMARY KEY (reacting_drug_id),
    UNIQUE (drugbank_id,reaction_id),   -- restrict the same tuple to be added multiple times
    FOREIGN KEY (drugbank_id) REFERENCES DrugBank(drugbank_id)
        ON UPDATE CASCADE  -- if a drug is updated, change it here also
  	    ON DELETE CASCADE, -- When a drug is deleted, it should be removed from (...) its corresponding entries from SIDER and BindingDB.

    FOREIGN KEY (reaction_id) REFERENCES BindingDB(reaction_id)
        ON UPDATE CASCADE   -- if a reaction is updated, change it here also
  	    ON DELETE CASCADE   -- if a reaction is deleted, delete the reaction-drug pair
);

-- no deletion anomaly
CREATE TABLE IF NOT EXISTS DrugSider
(
    drug_sider_id SERIAL,
    drugbank_id   TEXT NOT NULL,
    umls_cui      TEXT NOT NULL,
    PRIMARY KEY (drug_sider_id),
    UNIQUE (drugbank_id, umls_cui), -- restrict the same tuple to be added multiple times
    FOREIGN KEY (drugbank_id) REFERENCES DrugBank (drugbank_id)
        ON UPDATE CASCADE           -- if a reaction is updated, change it here also
        ON DELETE CASCADE,          -- When a drug is deleted, it should be removed from (...) its corresponding entries from SIDER and BindingDB.
    FOREIGN KEY (umls_cui) REFERENCES Sider (umls_cui)
        ON UPDATE CASCADE           -- if a side effect is updated, change it here also
        ON DELETE RESTRICT
);  -- do not allow a side effect in relation with a drug to be deleted


-- When a drug is deleted, it should be removed from the the list of the interacting drugs of other drugs,
-- and its corresponding entries from SIDER and BindingDB.
-- When a drug is deleted, we delete corresponding InteractingDrug, DrugSider and ReactingDrug entries using this trigger
CREATE OR REPLACE FUNCTION delete_rows_with_drugbank_id()
RETURNS trigger AS
$$
BEGIN
    DELETE FROM InteractingDrugs WHERE drug1 = OLD.drugbank_id OR drug2 = OLD.drugbank_id;
    DELETE FROM DrugSider WHERE DrugSider.drugbank_id = OLD.drugbank_id;
    DELETE FROM ReactingDrug WHERE ReactingDrug.drugbank_id = OLD.drugbank_id;
    RETURN OLD;
END;
$$
LANGUAGE plpgsql;

CREATE TRIGGER delete_drug_related_rows
AFTER DELETE ON DrugBank
FOR EACH ROW
    EXECUTE PROCEDURE delete_rows_with_drugbank_id();


-- We do not store drugbank_id in BindingDB, we store reaction_id - drugbank_id in another table ReactingDrug
-- So when a drug is deleted, we delete the corresponding rows from ReactingDrug using the above trigger.
-- and then, we delete the corresponding rows in BindingDB using this trigger
CREATE OR REPLACE FUNCTION delete_reaction_by_drug()
RETURNS trigger AS
$$
BEGIN
    DELETE FROM BindingDB WHERE reaction_id = OLD.reaction_id;
    RETURN OLD;
END;
$$
LANGUAGE plpgsql;

CREATE TRIGGER delete_drug_related_reaction
AFTER DELETE ON ReactingDrug
FOR EACH ROW
    EXECUTE PROCEDURE delete_reaction_by_drug();


-- When a protein is deleted, its corresponding entries from BindingDB should be removed.
-- We do not store uniprot_id in BindingDB, we store reaction_id - uniprot_id in another table ReactingProt
-- So when a protein is deleted, we delete the corresponding rows from ReactingProt using this trigger
CREATE OR REPLACE FUNCTION delete_rows_with_uniprot_id()
RETURNS trigger AS
$$
BEGIN
    DELETE FROM ReactingProt WHERE ReactingProt.uniprot_id = OLD.uniprot_id;
    RETURN OLD;
END;
$$
LANGUAGE plpgsql;

CREATE TRIGGER delete_protein_related_rows
AFTER DELETE ON Uniprot
FOR EACH ROW
    EXECUTE PROCEDURE delete_rows_with_uniprot_id();


-- When a protein is deleted, we delete the corresponding rows from ReactingProt using above trigger
-- and then, we delete the corresponding rows in BindingDB using this trigger
CREATE OR REPLACE FUNCTION delete_reaction_by_protein()
RETURNS trigger AS
$$
BEGIN
    DELETE FROM BindingDB WHERE reaction_id = OLD.reaction_id;
    RETURN OLD;
END;
$$
LANGUAGE plpgsql;

CREATE TRIGGER delete_protein_related_reaction
AFTER DELETE ON ReactingProt
FOR EACH ROW
    EXECUTE PROCEDURE delete_reaction_by_protein();


-- if there are 5 database managers in the system, prevent adding more
CREATE OR REPLACE FUNCTION database_manager_count_check()
RETURNS trigger AS
$$
BEGIN
  IF (cast((select count(*) from DatabaseManager) as int) = 5) THEN
    RAISE EXCEPTION 'Database Manager count cannot exceed 5.';
  END IF;
  RETURN NEW;
END;
$$
LANGUAGE plpgsql;

CREATE TRIGGER database_manager_count
BEFORE INSERT ON DatabaseManager
FOR EACH ROW
    EXECUTE PROCEDURE database_manager_count_check();


CREATE OR REPLACE FUNCTION insert_institutions()
RETURNS trigger AS
$$
BEGIN
  IF (new.institution not in
      (select institution from institutionpoints)) THEN
    INSERT INTO InstitutionPoints(institution, points) VALUES (new.institution, 0);
  END IF;
  RETURN NEW;
END;
$$
LANGUAGE plpgsql;

CREATE TRIGGER insert_institutions
AFTER INSERT ON Users
FOR EACH ROW
    EXECUTE PROCEDURE insert_institutions();

-- When a new publication is added to the system, the corresponding institute gets 5 points for a new publication
-- and gets 2 points for each individual who contributed to it.
-- Also, when there is an update on the publication that changes the number of contributors,
-- update the corresponding institute’s score accordingly.
-- DİKKAT : UPDATEDE ONCE HEPSİNİ SİLERSEK PATLIYO
CREATE OR REPLACE FUNCTION increase_institution_points()
RETURNS trigger AS
$$
BEGIN
    IF (cast(
        (select count(*) from ArticleAuthor WHERE NEW.article_doi=article_doi)
        as int) = 0)
        -- this article is just added

        THEN WITH my_query as (SELECT * from InstitutionPoints
                               WHERE institution = (
                                   SELECT institution FROM users
                                   WHERE NEW.author_id = user_id)
                                )
        UPDATE InstitutionPoints
        SET points = (SELECT points from my_query) + 7
        WHERE institution = (SELECT institution from my_query);

    ELSE

        WITH my_query as (SELECT * from InstitutionPoints
                               WHERE institution = (
                                   SELECT institution FROM users
                                   WHERE NEW.author_id = user_id)
                                )
        UPDATE InstitutionPoints
        SET points = (SELECT points from my_query) + 2
        WHERE institution = (SELECT institution from my_query);
  END IF;
  RETURN NEW;
END;
$$
LANGUAGE plpgsql;

CREATE TRIGGER article_points
BEFORE INSERT ON ArticleAuthor
FOR EACH ROW
    EXECUTE PROCEDURE increase_institution_points();


-- stored procedure
-- Users shall be able to filter interacting targets of a specific drug
-- considering the selected measurement type and the range of the affinity values.
-- This must be implemented as a stored procedure.
-- Parameters of this procedure are measurement type, minimum affinity value, and maximum affinity value.

CREATE OR REPLACE FUNCTION filter_targets
    (d/*drug_id*/ TEXT, m /*measure*/TEXT, k/*min affinity*/ REAL, z/*max affinity*/ REAL)
    RETURNS TABLE (uniprot_id TEXT, protein_name TEXT, sequence TEXT)

AS
    $$
    BEGIN
        RETURN QUERY
        SELECT Uniprot.uniprot_id, Uniprot.protein_name, Uniprot.sequence
        FROM Uniprot,
            (SELECT ReactingProt.uniprot_id 
            FROM ReactingProt,
                (SELECT reaction_id 
                FROM BindingDB B,
                    (SELECT reaction_id as rid FROM ReactingDrug WHERE drugbank_id = d) D
                WHERE B.measure = m AND B.affinity >= k AND B.affinity <= z AND reaction_id = D.rid) R
            WHERE R.reaction_id = ReactingProt.reaction_id) U
        WHERE Uniprot.uniprot_id = U.uniprot_id;
    END
    $$
LANGUAGE plpgsql;
