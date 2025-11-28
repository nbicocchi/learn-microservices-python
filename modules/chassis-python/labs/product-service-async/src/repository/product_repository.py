from typing import List, Optional
from sqlmodel import select
from sqlmodel.ext.asyncio.session import AsyncSession

from models.product import Product
from schemas.product import ProductCreate, ProductUpdate


class ProductRepository:

    def __init__(self, session: AsyncSession):
        self.session = session

    async def create(self, data: ProductCreate) -> Product:
        product = Product(uuid=data.uuid, name=data.name, weight=data.weight)
        self.session.add(product)
        await self.session.commit()
        await self.session.refresh(product)
        return product

    async def get_all(self) -> List[Product]:
        result = await self.session.execute(select(Product))
        return result.scalars().all()

    async def get_by_id(self, product_id: int) -> Optional[Product]:
        return await self.session.get(Product, product_id)

    async def update(self, product_id: int, data: ProductUpdate) -> Optional[Product]:
        product = await self.get_by_id(product_id)
        if not product:
            return None

        if data.uuid is not None:
            product.uuid = data.uuid
        if data.name is not None:
            product.name = data.name
        if data.weight is not None:
            product.weight = data.weight

        self.session.add(product)
        await self.session.commit()
        await self.session.refresh(product)
        return product

    async def delete(self, product_id: int) -> bool:
        product = await self.get_by_id(product_id)
        if not product:
            return False

        await self.session.delete(product)
        await self.session.commit()
        return True
