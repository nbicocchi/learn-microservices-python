from repository.product_repository import ProductRepository
from schemas.product import ProductCreate, ProductUpdate

class ProductService:

    def __init__(self, repo: ProductRepository):
        self.repo = repo

    def create_product(self, data: ProductCreate):
        return self.repo.create(data)

    def list_products(self):
        return self.repo.get_all()

    def get_product(self, product_id: int):
        return self.repo.get_by_id(product_id)

    def update_product(self, product_id: int, data: ProductUpdate):
        return self.repo.update(product_id, data)

    def delete_product(self, product_id: int) -> bool:
        return self.repo.delete(product_id)
