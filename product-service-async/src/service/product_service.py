from repository.product_repository import ProductRepository
from schemas.product import ProductCreate, ProductUpdate

class ProductService:

    def __init__(self, repo: ProductRepository):
        self.repo = repo

    async def create_product(self, data: ProductCreate):
        return await self.repo.create(data)

    async def list_products(self):
        return await self.repo.get_all()

    async def get_product(self, product_id: int):
        return await self.repo.get_by_id(product_id)

    async def update_product(self, product_id: int, data: ProductUpdate):
        return await self.repo.update(product_id, data)

    async def delete_product(self, product_id: int) -> bool:
        return await self.repo.delete(product_id)
