import sys; sys.path.insert(0,'/mnt/c/Users/ha/Downloads/pwn')
from fs import *
g=FS('god'); g.name(b'AAAA')
c=g.chef(); print('chef', {k:c[k] for k in ('level','power','money')})
# add a recipe at level>=2 using ingredient index 0 (Egg)
m=g.add_recipe(b'RECIPE_A',[b'0']); print('magic A', m)
m=g.add_recipe(b'RECIPE_B',[b'0']); print('magic B', m)
print('show:\n'+g.show_recipe().decode(errors='replace'))
g.close()
