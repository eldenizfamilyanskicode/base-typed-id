import inspect

import base_typed_id
from base_typed_id import BasePrefixedTypedId, BaseTypedId

print("file:", base_typed_id.__file__)
print("version:", base_typed_id.__version__)
print("BaseTypedId.__reduce__:", inspect.signature(BaseTypedId.__reduce__))
print(
    "BasePrefixedTypedId.__reduce__:", inspect.signature(BasePrefixedTypedId.__reduce__)
)
