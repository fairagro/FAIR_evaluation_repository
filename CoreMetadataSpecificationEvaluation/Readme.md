# FAIR Assessment evaluation of Core Metadata Specification implementation
This folder contains metadata instances of FAIRagro RDIs manually annotated with recommenations of the Core Metadata Specification to enable the evaluation its influence on FAIR Assessment tools
The initial example metadata instance was taken from the [FAIRagro Middleware](https://github.com/fairagro/middleware_repo) 

Example dataset: https://doi.org/10.3220/253-2025-211

As not all metadata required for the CMS were available, some information was made up:
- the authors are affiliated with a specific institute of Thünen Institute, which do not have ROR ids. To evaluate how ROR ideas influence FAIR scores, the ROR id of the whole Thünen Institute was added, which is not the same as the specific sub-institute.
- No author is clearly marked as a point of contact. To model this information, the first author of the list was treated as if.
- Existing identifiers of authors were enriched with identifiers.org links for values of propertyID instances
- Resolvable strings of existing identifiers were removed
- The general Thünen Institute email address was added to the affiliaton metadata
- No email adresses for authors were available so fictional example email adresses were added
- The DefinedTerm for "agricultural sciences" was added 
- keywords were not available in the original schema.org metadata instance, but in the original repository metadata. They were added to the extended JSON instance and terminology metadata was added to one keywords because it was available
- The mainEntityOfPage property was replaced with the url property
- As no version information was available, the dataset was assumed to be version 1.0
- encodingFormat was inferred from filetype on repository landing page
- the spatial coverage was inferred from the description of the dataset and added as a Country (subtype of Place)
- No bounding box was available
- dcterms:accesRights were inferred as "open access" due to an open license in the metadata
- also "isAccessibleForFree": "True" was added due to this reason
