rm(list=ls(all=TRUE)) 
library(jsonlite)
library(XML)
library(yaml)
library(readr)
library(stringr)
library(plyr)
library(dplyr)


############################################################################  DOWNLOAD JSON FILES IN REALTIME ###########################################################################
#########################################################################################################################################################################################

cat("Downloading - OBO Foundry...")
download.file("http://www.obofoundry.org/registry/ontologies.jsonld", "/Users/davidodgers/Desktop/biohack/operations/dumps/obo_foundry.jsonld", "wget", quiet = TRUE, mode = "w", cacheOK = TRUE, extra = getOption("download.file.extra"))
cat("DONE!\n")

cat("Downloading - Bioportal...")
download.file("http://data.bioontology.org/ontologies?apikey=ee0c3414-57d8-46ed-a31b-49423df3a1b3", "/Users/davidodgers/Desktop/biohack/operations/dumps/bioportal.jsonld", "wget", quiet = TRUE, mode = "w", cacheOK = TRUE, extra = getOption("download.file.extra"))
cat("DONE!\n")

cat("Downloading - Bioportal Resources...")
download.file("http://data.bioontology.org/resource_index/resources/?apikey=ee0c3414-57d8-46ed-a31b-49423df3a1b3", "/Users/davidodgers/Desktop/biohack/operations/dumps/bioportal_resources.jsonld", "wget", quiet = TRUE, mode = "w", cacheOK = TRUE, extra = getOption("download.file.extra"))
cat("DONE!\n")

cat("Downloading - Prefix.CC...")
download.file("http://prefix.cc/context", "/Users/davidodgers/Desktop/biohack/operations/dumps/prefix_cc.jsonld", "wget", quiet = TRUE, mode = "w", cacheOK = TRUE, extra = getOption("download.file.extra"))
cat("DONE!\n")

cat("Downloading - Linked Open Vocabularies...")
download.file("http://lov.okfn.org/dataset/lov/api/v2/vocabulary/list", "/Users/davidodgers/Desktop/biohack/operations/dumps/linked_open_vocabularies.jsonld", "wget", quiet = TRUE, mode = "w", cacheOK = TRUE, extra = getOption("download.file.extra"))
cat("DONE!\n")

cat("Downloading - Gene Ontology Prefix Registry...")
download.file("https://raw.githubusercontent.com/geneontology/go-site/master/metadata/db-xrefs.yaml", "/Users/davidodgers/Desktop/biohack/operations/dumps/gene_ontology_prefix.yaml", "wget", quiet = TRUE, mode = "w", cacheOK = TRUE, extra = getOption("download.file.extra"))
cat("DONE!\n")

############################################################################  CREATE JSON FILENAMES FOR LATER USE #######################################################################
#########################################################################################################################################################################################

json_obo_foundry<-"/Users/davidodgers/Desktop/biohack/operations/dumps/obo_foundry.jsonld"
json_bioportal<-"/Users/davidodgers/Desktop/biohack/operations/dumps/bioportal.jsonld"
json_bioportal_resources<-"/Users/davidodgers/Desktop/biohack/operations/dumps/bioportal_resources.jsonld"
json_prefix_cc<-"/Users/davidodgers/Desktop/biohack/operations/dumps/prefix_cc.jsonld"
json_linked_open_vocabularies<-"/Users/davidodgers/Desktop/biohack/operations/dumps/linked_open_vocabularies.jsonld"
json_gene_ontology_prefix<-"/Users/davidodgers/Desktop/biohack/operations/dumps/gene_ontology_prefix.yaml"

############################################################################  PARSE FILES INTO DATAFRAMES ###############################################################################
#########################################################################################################################################################################################

parsed_obo_foundry<-fromJSON(json_obo_foundry)
parsed_bioportal<-fromJSON(json_bioportal)
parsed_bioportal_resources<-fromJSON(json_bioportal_resources)
parsed_prefix_cc<-fromJSON(json_prefix_cc)
parsed_linked_open_vocabularies<-fromJSON(json_linked_open_vocabularies)


###yaml suff
parsed_gene_ontology_prefix<-yaml.load_file(json_gene_ontology_prefix)
#parsed_gene_ontology_prefix<-yaml.load(str_replace(read_file(json_gene_ontology_prefix),"\"",""), as.named.list = TRUE, handlers = NULL)

#test<-read_file(json_gene_ontology_prefix)
#test1<-gsub("\\\.","",read_file(json_gene_ontology_prefix))
#yaml.load(test, as.named.list = FALSE, handlers = NULL)

#parsed_biosharing<-fromJSON(json_biosharing)

############################################################################  CREATE DATAFRAMES FROM JSON  ##############################################################################
#########################################################################################################################################################################################

final_column_names<-c("Original Position",
                      "Primary Prefix",
                      "Alternate Prefix",
                      "Local Identifier",
                      "Entity Identifier (e.g., IRI)",
                      "Identifier namespace path if different",
                      "Identifier Resolution - Computable (y/n)",
                      "Identifier Resolution - Human Viewable (y/n)",
                      "Alternate Namespace for Human Readable Pages",
                      "Homepage",
                      "Description",
                      "Title",
                      "Source")



final_column_position<-c(
  "Original Position",
  "Source",
  "Primary Prefix",	
  "Alternate Prefix",
  "Local Identifier",
  "Entity Identifier (e.g., IRI)",
  "Identifier namespace path if different",
  "Identifier Resolution - Computable (y/n)",
  "Identifier Resolution - Human Viewable (y/n)",
  "Alternate Namespace for Human Readable Pages",
  "Homepage",
  "Description",
  "Title")

##################################OBO Foundry Dataframes
obo_foundry_browsers<-parsed_obo_foundry$ontologies$browsers

obo_foundry_primary_prefix<-data.frame(original_position=numeric(),primary_prefix=character())
obo_foundry_human_url<-data.frame(original_position=numeric(),human_url=character())
obo_foundry_title<-data.frame(original_position=numeric(),title=character())
obo_foundry_homepage<-data.frame(original_position=numeric(),homepage=character())

obo_foundry_alternate_prefix<-data.frame(alternate_prefix=parsed_obo_foundry$ontologies$alternatePrefix)
obo_foundry_description<-data.frame(description=parsed_obo_foundry$ontologies$description)
obo_foundry_namespace_if_diff<-data.frame(namespace_if_different=parsed_obo_foundry$ontologies$ontology_purl)
obo_foundry_entity_identifier<-data.frame(entity_identifier=parsed_obo_foundry$ontologies$ontology_purl)
obo_foundry_local_identifier<-data.frame(local_identifier=parsed_obo_foundry$ontologies$id)

for(i in 1:length(obo_foundry_browsers)){
  cur_row<-obo_foundry_browsers[[i]]
  cur_primary_prefix<-cur_row$label
  cur_human_url<-cur_row$url
  cur_title<-cur_row$title
  cur_homepage<-parsed_obo_foundry$ontologies$homepage[[i]]
  
  if(is.null(cur_primary_prefix)){
    obo_foundry_primary_prefix<-rbind(obo_foundry_primary_prefix,data.frame(original_position=i,primary_prefix=""))
  }else{
    obo_foundry_primary_prefix<-rbind(obo_foundry_primary_prefix,data.frame(original_position=i,primary_prefix=cur_primary_prefix))
  }
  
  if(is.null(cur_human_url)){
    obo_foundry_human_url<-rbind(obo_foundry_human_url,data.frame(original_position=i,human_url=""))
  }else{
    obo_foundry_human_url<-rbind(obo_foundry_human_url,data.frame(original_position=i,human_url=cur_human_url))
  }
  
  if(is.null(cur_title)){
    obo_foundry_title<-rbind(obo_foundry_title,data.frame(original_position=i,title=""))
  }else{
    obo_foundry_title<-rbind(obo_foundry_title,data.frame(original_position=i,title=cur_title))
  }
  
  if(is.null(cur_homepage)){
    obo_foundry_homepage<-rbind(obo_foundry_homepage,data.frame(original_position=i,homepage=""))
  }else{
    obo_foundry_homepage<-rbind(obo_foundry_homepage,data.frame(original_position=i,homepage=cur_homepage))
  }
}

obo_foundry_unnumbered<-data.frame(obo_foundry_alternate_prefix, obo_foundry_local_identifier, obo_foundry_entity_identifier, obo_foundry_namespace_if_diff, obo_foundry_description)
obo_foundry_unnumbered$original_position<-row.names(obo_foundry_unnumbered)

obo_foundary_numbered<-merge(obo_foundry_primary_prefix, obo_foundry_human_url, by="original_position")
obo_foundary_numbered<-merge(obo_foundary_numbered, obo_foundry_homepage, by="original_position")
obo_foundary_numbered<-merge(obo_foundary_numbered, obo_foundry_title, by="original_position")

complete_obo_foundry<-merge(obo_foundary_numbered, obo_foundry_unnumbered, by="original_position")
complete_obo_foundry$resolution_computable<-""
complete_obo_foundry$resolution_human<-""
complete_obo_foundry$source_URL<-""

complete_obo_foundry<-complete_obo_foundry[c("original_position",
                                             "primary_prefix",
                                             "alternate_prefix",
                                             "local_identifier",
                                             "entity_identifier",
                                             "namespace_if_different",
                                             "resolution_computable",
                                             "resolution_human",
                                             "human_url",
                                             "homepage",
                                             "description",
                                             "title",
                                             "source_URL")]

names(complete_obo_foundry)<-final_column_names

complete_obo_foundry<-complete_obo_foundry[final_column_position]

##################################Bioportal Dataframes
bioportal_primary_prefix<-parsed_bioportal$acronym
bioportal_title<-parsed_bioportal$name
complete_bioportal<-data.frame(primary_prefix=bioportal_primary_prefix, title=bioportal_title)

complete_bioportal$original_position<-row.names(complete_bioportal)
complete_bioportal$alternate_prefix<-""
complete_bioportal$local_identifier<-""
complete_bioportal$entity_identifier<-""
complete_bioportal$namespace_if_different<-""
complete_bioportal$resolution_computable<-""
complete_bioportal$resolution_human<-""
complete_bioportal$human_url<-""
complete_bioportal$homepage<-""
complete_bioportal$description<-""
complete_bioportal$source_URL<-""

complete_bioportal<-complete_bioportal[c("original_position",
                                         "primary_prefix",
                                         "alternate_prefix",
                                         "local_identifier",
                                         "entity_identifier",
                                         "namespace_if_different",
                                         "resolution_computable",
                                         "resolution_human",
                                         "human_url",
                                         "homepage",
                                         "description",
                                         "title",
                                         "source_URL")]

names(complete_bioportal)<-final_column_names

complete_bioportal<-complete_bioportal[final_column_position]

##################################Bioportal Resources Dataframes
bioportal_resources_primary_prefix<-parsed_bioportal_resources$acronym
bioportal_resources_local_identifier<-parsed_bioportal_resources$id
bioportal_resources_namespace_if_different<-parsed_bioportal_resources$lookupURL
bioportal_resources_homepage<-parsed_bioportal_resources$homepage
bioportal_resources_description<-parsed_bioportal_resources$description
bioportal_resources_title<-parsed_bioportal_resources$name

complete_bioportal_resources<-data.frame(primary_prefix=bioportal_resources_primary_prefix, 
                                         local_identifier=bioportal_resources_local_identifier, 
                                         namespace_if_different=bioportal_resources_namespace_if_different,
                                         homepage=bioportal_resources_homepage,
                                         description=bioportal_resources_description,
                                         title=bioportal_resources_title)

complete_bioportal_resources$original_position<-row.names(complete_bioportal_resources)
complete_bioportal_resources$alternate_prefix<-""
complete_bioportal_resources$entity_identifier<-""
complete_bioportal_resources$resolution_computable<-""
complete_bioportal_resources$resolution_human<-""
complete_bioportal_resources$human_url<-""
complete_bioportal_resources$source_URL<-""

complete_bioportal_resources<-complete_bioportal_resources[c("original_position",
                                                             "primary_prefix",
                                                             "alternate_prefix",
                                                             "local_identifier",
                                                             "entity_identifier",
                                                             "namespace_if_different",
                                                             "resolution_computable",
                                                             "resolution_human",
                                                             "human_url",
                                                             "homepage",
                                                             "description",
                                                             "title",
                                                             "source_URL")]


names(complete_bioportal_resources)<-final_column_names

complete_bioportal_resources<-complete_bioportal_resources[final_column_position]


##################################Prefix.cc Dataframes
prefix_cc_key_val<-parsed_prefix_cc$'@context'

prefix_cc_primary_prefix<-paste(prefix_cc_key_val)
prefix_cc_entity_identifier<-paste(names(prefix_cc_key_val))
prefix_cc_namespace_if_different<-paste(names(prefix_cc_key_val))

complete_prefix_cc<-data.frame(primary_prefix=prefix_cc_primary_prefix, entity_identifier=prefix_cc_entity_identifier, namespace_if_different=prefix_cc_namespace_if_different)
complete_prefix_cc$original_position<-row.names(complete_prefix_cc)

complete_prefix_cc$alternate_prefix<-""
complete_prefix_cc$local_identifier<-""
complete_prefix_cc$resolution_computable<-""
complete_prefix_cc$resolution_human<-""
complete_prefix_cc$human_url<-""
complete_prefix_cc$homepage<-""
complete_prefix_cc$description<-""
complete_prefix_cc$title<-""
complete_prefix_cc$source_URL<-""

complete_prefix_cc<-complete_prefix_cc[c("original_position",
                                         "primary_prefix",
                                         "alternate_prefix",
                                         "local_identifier",
                                         "entity_identifier",
                                         "namespace_if_different",
                                         "resolution_computable",
                                         "resolution_human",
                                         "human_url",
                                         "homepage",
                                         "description",
                                         "title",
                                         "source_URL")]

names(complete_prefix_cc)<-final_column_names

complete_prefix_cc<-complete_prefix_cc[final_column_position]


##################################Linked Open Vocabularies Dataframes
linked_open_vocabularies_primary_prefix<-parsed_linked_open_vocabularies$prefix
linked_open_vocabularies_entity_identifier<-parsed_linked_open_vocabularies$uri
linked_open_vocabularies_namespace_if_different<-parsed_linked_open_vocabularies$nsp
linked_open_vocabularies_title<-data.frame(original_position=numeric(), title=character())

titles<-parsed_linked_open_vocabularies$titles

for(i in 1:length(titles)){
  cur_title<-titles[[i]]$value
  linked_open_vocabularies_title<-rbind(linked_open_vocabularies_title, data.frame(original_position=i,title=cur_title))
}

linked_open_vocabularies_tmp<-data.frame(primary_prefix=linked_open_vocabularies_primary_prefix,
                                         entity_identifier=linked_open_vocabularies_entity_identifier,
                                         namespace_if_different=linked_open_vocabularies_namespace_if_different
)

linked_open_vocabularies_tmp$original_position<-row.names(linked_open_vocabularies_tmp)
linked_open_vocabularies_tmp$alternate_prefix<-""
linked_open_vocabularies_tmp$local_identifier<-""
linked_open_vocabularies_tmp$resolution_computable<-""
linked_open_vocabularies_tmp$resolution_human<-""
linked_open_vocabularies_tmp$human_url<-""
linked_open_vocabularies_tmp$human_url<-""
linked_open_vocabularies_tmp$homepage<-""
linked_open_vocabularies_tmp$description<-""
linked_open_vocabularies_tmp$source_URL<-""

complete_linked_open_vocabularies<-merge(linked_open_vocabularies_title, linked_open_vocabularies_tmp, by = "original_position")

complete_linked_open_vocabularies<-complete_linked_open_vocabularies[c("original_position",
                                                                       "primary_prefix",
                                                                       "alternate_prefix",
                                                                       "local_identifier",
                                                                       "entity_identifier",
                                                                       "namespace_if_different",
                                                                       "resolution_computable",
                                                                       "resolution_human",
                                                                       "human_url",
                                                                       "homepage",
                                                                       "description",
                                                                       "title",
                                                                       "source_URL")]

names(complete_linked_open_vocabularies)<-final_column_names

complete_linked_open_vocabularies<-complete_linked_open_vocabularies[final_column_position]


##################################Gene Ontology Prefix Registry Dataframes



############################################################################  SAVE DATAFRAMES AS CSV  ##############################################################################
#########################################################################################################################################################################################

write.csv(complete_bioportal, file = "/Users/davidodgers/Desktop/biohack/operations/csv/complete_bioportal.csv")
write.csv(complete_bioportal_resources, file = "/Users/davidodgers/Desktop/biohack/operations/csv/complete_bioportal_resources.csv")
write.csv(complete_linked_open_vocabularies, file = "/Users/davidodgers/Desktop/biohack/operations/csv/complete_linked_open_vocabularies.csv")
write.csv(complete_obo_foundry, file = "/Users/davidodgers/Desktop/biohack/operations/csv/complete_obo_foundry.csv")
write.csv(complete_prefix_cc, file = "/Users/davidodgers/Desktop/biohack/operations/csv/complete_prefix_cc.csv")




