from typing import List, Optional
from sqlmodel import Session, select
from models.product import Product
from schemas.product import ProductCreate, ProductUpdate

class ProductRepository:

    def __init__(self, session: Session):
        self.session = session

    def create(self, data: ProductCreate) -> Product:
        product = Product(uuid=data.uuid, name=data.name, weight=data.weight)
        self.session.add(product)
        self.session.commit()
        self.session.refresh(product)
        return product

    def get_all(self) -> List[Product]:
        return self.session.exec(select(Product)).all()

    def get_by_id(self, product_id: int) -> Optional[Product]:
        return self.session.get(Product, product_id)

    def update(self, product_id: int, data: ProductUpdate) -> Optional[Product]:
        product = self.get_by_id(product_id)
        if not product:
            return None
        if data.uuid is not None:
            product.uuid = data.uuid
        if data.name is not None:
            product.name = data.name
        if data.weight is not None:
            product.weight = data.weight
        self.session.add(product)
        self.session.commit()
        self.session.refresh(product)
        return product

    def delete(self, product_id: int) -> bool:
        product = self.get_by_id(product_id)
        if not product:
            return False
        self.session.delete(product)
        self.session.commit()
        return True
