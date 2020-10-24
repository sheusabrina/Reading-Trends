import isbnlib
from isbnlib import meta, is_isbn10, is_isbn13

hp_isbn = "9780545010221"

print(is_isbn13(hp_isbn))
print(meta(hp_isbn)) # RETURNS DATA WE ALREADY KNOW
