
# # download kegg data
# kegg rest api: http://rest.kegg.jp
# - pathway list: http://rest.kegg.jp/list/pathway
# - ko list: http://rest.kegg.jp/list/pathway/ko
# - link of pathway and ko: http://rest.kegg.jp/link/pathway/ko
# - pathway image: http://rest.kegg.jp/get/map00030/image
# - pathway conf: http://rest.kegg.jp/get/map00030/conf
mkdir -p keggdb/pathway

if [ ! -f pathway.list ];then
  wget -c http://rest.kegg.jp/list/pathway -O pathway.list
fi

for map in $(grep -oP 'map\d+' pathway.list);do

echo wget -c http://rest.kegg.jp/get/$map/image -O keggdb/pathway/$map.png
echo wget -c http://rest.kegg.jp/get/$map/conf -O keggdb/pathway/$map.conf

done | parallel -j 4

