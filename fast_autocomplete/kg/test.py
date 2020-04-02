from fast_autocomplete import AutoComplete
words = {"blip": {}, "cat":{}, "catnip":{}, "cats":{}, "bli":{}}
autocomplete = AutoComplete(words=words)
print(autocomplete.search("cam",size=10))
