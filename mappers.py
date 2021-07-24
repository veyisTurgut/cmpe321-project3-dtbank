import re
from schemas import *


def sider_mapper(sider: tuple) -> Sider:
    return Sider(
        umls_cui=sider[0],
        side_effect_name=sider[1]
    )


def user_mapper(user: tuple) -> User:
    return User(
        user_id=user[0],
        username=user[1],
        institution=user[2],
        password=user[3]
    )


def user_confidential_mapper(user_confidential: tuple) -> UserConfidential:
    return UserConfidential(
        username=user_confidential[0],
        institution=user_confidential[1],
        realname=user_confidential[2]
    )


def uniprot_mapper(uniprot: tuple) -> Uniprot:
    return Uniprot(
        uniprot_id=uniprot[0],
        target_name=uniprot[1],
        sequence=uniprot[2]
    )


def drugs_protein_mapper(input: dict) -> DrugsProteinResponse:
    return DrugsProteinResponse(
        uniprot_id=input["uniprot_id"],
        protein_name=input["protein_name"],
        sequence=input["sequence"],
        drugs=input["drugs"]
    )


def drug_sider_mapper(drug_sider: tuple) -> DrugSider:
    return DrugSider(
        drugbank_id=drug_sider[0],
        drug_name=drug_sider[1],
        smiles=drug_sider[2],
        description=drug_sider[3],
        side_effect_names=[tup[0] for tup in drug_sider[-1]],
        target_names=[tup[0] for tup in drug_sider[-2]]
    )


def drug_mapper(drug: tuple) -> Drug:
    return Drug(
        drugbank_id=drug[0],
        drug_name=drug[1],
        smiles=drug[2],
        description=drug[3]
    )

def drug_point_mapper(drug: tuple) -> DrugSideNumber:
    return DrugSideNumber(
        drugbank_id=drug[0],
        drug_name=drug[1],
        smiles=drug[2],
        description=drug[3],
        number_of_side_effects = drug[4]
    )

def interacting_drug_mapper(drug: tuple) -> InteractingDrug:
    return InteractingDrug(
        drugbank_id=drug[0],
        drug_name=drug[1]
    )   


def article_mapper(article: tuple) -> Article:
    return Article(
        doi=article[0],
        contributors=article[1],
    )


def institution_point_mapper(institution_point: tuple) -> InstitutionPoint:
    return InstitutionPoint(
        institution=institution_point[0],
        point=institution_point[1]
    )


def reaction_mapper(reaction: tuple) -> Reaction:
    return Reaction(
        reaction_id=reaction[0],
        measure=reaction[1],
        affinity=reaction[2],
        article_doi=reaction[3]
    )


def drugtarget_mapper(drugtarget: tuple) -> DrugTarget:
    return DrugTarget(
        drugbank_id=drugtarget[0],
        uniprot_id=drugtarget[1]
    )
