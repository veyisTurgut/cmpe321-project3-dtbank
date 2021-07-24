from typing import List

from pydantic import BaseModel
from pydantic.types import PositiveInt


class CreateUser(BaseModel):
    username: str
    realname: str
    institution: str
    password: str


class User(BaseModel):
    user_id: int
    realname: str
    username: str
    institution: str
    password: str


class UserResponse(BaseModel):
    items: List[User]


class UserConfidential(BaseModel):
    realname: str
    username: str
    institution: str


class UserConfidentialResponse(BaseModel):
    items: List[UserConfidential]


class Sider(BaseModel):
    umls_cui: str
    side_effect_name: str


class SiderResponse(BaseModel):
    items: List[Sider]


class InteractingDrug(BaseModel):
    drugbank_id: str
    drug_name: str


class InteractingDrugListResponse(BaseModel):
    items: List[InteractingDrug]


class Uniprot(BaseModel):
    uniprot_id: str
    target_name: str
    sequence: str


class DrugsProteinResponse(BaseModel):
    uniprot_id: str
    protein_name: str
    sequence: str
    drugs: List[dict]


class UniprotResponse(BaseModel):
    items: List[Uniprot]


class DrugSider(BaseModel):
    drugbank_id: str
    drug_name: str
    description: str
    smiles: str
    side_effect_names: List[str]
    target_names: List[str]


class Drug(BaseModel):
    drugbank_id: str
    drug_name: str
    description: str
    smiles: str

class DrugSideNumber(BaseModel):
    drugbank_id: str
    drug_name: str
    description: str
    smiles: str
    number_of_side_effects: int

class DrugSiderResponse(BaseModel):
    items: List[DrugSider]


class DrugResponse(BaseModel):
    items: List[Drug]


class DrugSideNumberResponse(BaseModel):
    items: List[DrugSideNumber]

class Article(BaseModel):
    doi: str
    contributors: List[str]


class ArticleResponse(BaseModel):
    items: List[Article]


class DMLoginCredentials(BaseModel):
    username: str
    password: str


class UserLoginCredentials(BaseModel):
    username: str
    institution: str
    password: str


class InstitutionPoint(BaseModel):
    institution: str
    point: int


class InstitutionPointResponse(BaseModel):
    items: List[InstitutionPoint]


class Reaction(BaseModel):
    reaction_id: int
    measure: str
    affinity: float
    article_doi: str


class ReactionResponse(BaseModel):
    items: List[Reaction]


class Author(BaseModel):
    realname: str
    username: str
    password: str


class DrugTarget(BaseModel):
    drugbank_id: str
    uniprot_id: str


class DrugTargetResponse(BaseModel):
    items: List[DrugTarget]
