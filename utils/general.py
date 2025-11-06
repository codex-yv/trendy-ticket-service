from security.decryptAmt import decryptt
from security.encrypyAmt import encryptt


async def get_amount(mesh:str):
    try:
        amount_mesh = mesh.split("#")[1]
        key_mesh = mesh.split("#")[-1]
        amount_en = amount_mesh.encode()

        data = await decryptt(token=amount_en, key= key_mesh.encode())
        return str(data)
    except IndexError:
        pass
