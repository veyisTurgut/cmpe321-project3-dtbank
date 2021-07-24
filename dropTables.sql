
DROP FUNCTION IF EXISTS filter_targets;

DROP TRIGGER IF EXISTS article_points ON articleauthor;
DROP FUNCTION IF EXISTS increase_institution_points();

DROP TRIGGER IF EXISTS insert_institutions ON users;
DROP FUNCTION IF EXISTS insert_institutions();

DROP TRIGGER IF EXISTS database_manager_count ON databasemanager;
DROP FUNCTION IF EXISTS database_manager_count_check();

DROP TRIGGER IF EXISTS delete_protein_related_reaction ON reactingprot;
DROP FUNCTION IF EXISTS delete_reaction_by_protein();

DROP TRIGGER IF EXISTS delete_protein_related_rows ON Uniprot;
DROP FUNCTION IF EXISTS delete_rows_with_uniprot_id();

DROP TRIGGER IF EXISTS  delete_drug_related_reaction ON ReactingDrug;
DROP FUNCTION IF EXISTS delete_reaction_by_drug();

DROP TRIGGER IF EXISTS delete_drug_related_rows ON DrugBank;
DROP FUNCTION IF EXISTS delete_rows_with_drugbank_id();

DROP TABLE IF EXISTS ArticleAuthor;
DROP TABLE IF EXISTS DrugSider;
DROP TABLE IF EXISTS ReactingDrug;
DROP TABLE IF EXISTS ReactingProt;
DROP TABLE IF EXISTS InteractingDrugs;
DROP TABLE IF EXISTS BindingDB;
DROP TABLE IF EXISTS Article;
DROP TABLE IF EXISTS DrugBank;
DROP TABLE IF EXISTS Uniprot;
DROP TABLE IF EXISTS Users;
DROP TABLE IF EXISTS Sider;
DROP TABLE IF EXISTS DatabaseManager;
DROP TABLE IF EXISTS InstitutionPoints;


