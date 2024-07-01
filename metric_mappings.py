# metric_mappings.py

from rdflib import Namespace

FAIRAGRO = Namespace("https://fairagro.net/ontology#")

fes_metric_mapping = {
    "category": FAIRAGRO["FAIRDataQuality"],
    "dimensions": {
        "findability": {
            "dimension_uri": FAIRAGRO["findability"],
            "definition": "The degree to which data is easy to find for both humans and computers. Metadata and data should be easy to discover with search mechanisms and be uniquely identifiable using standard identifiers.",
            "metrics": [
                FAIRAGRO["FES-UniqueIdentifierMetric"],
                FAIRAGRO["FES-IdentifierPersistenceMetric"],
                FAIRAGRO["FES-DataIdentifierPersistenceMetric"],
                FAIRAGRO["FES-StructuredMetadataMetric"],
                FAIRAGRO["FES-GroundedMetadataMetric"],
                FAIRAGRO["FES-DataIdentifierExplicitlyInMetadataMetric"],
                FAIRAGRO["FES-MetadataIdentifierExplicitlyInMetadataMetric"],
                FAIRAGRO["FES-SearchableInMajorSearchEngineMetric"]
            ]
        },
        "accessibility": {
            "dimension_uri": FAIRAGRO["accessibility"],
            "definition": "The degree to which data is retrievable and accessible by authorized individuals or systems. This includes providing metadata that allows data to be accessed through well-defined protocols.",
            "metrics": [
                FAIRAGRO["FES-OpenFreeProtocolDataRetrievalMetric"],
                FAIRAGRO["FES-OpenFreeProtocolMetadataRetrievalMetric"],
                FAIRAGRO["FES-DataAuthenticationAuthorizationMetric"],
                FAIRAGRO["FES-MetadataAuthenticationAuthorizationMetric"],
                FAIRAGRO["FES-MetadataPersistenceMetric"]
            ]
        },
        "interoperability": {
            "dimension_uri": FAIRAGRO["interoperability"],
            "definition": "The degree to which data is able to be integrated with other data and systems. This involves using shared vocabularies, ontologies, and standards to enable data exchange and reuse across different contexts.",
            "metrics": [
                FAIRAGRO["FES-MetadataKnowledgeRepresentationLanguageWeakMetric"],
                FAIRAGRO["FES-MetadataKnowledgeRepresentationLanguageStrongMetric"],
                FAIRAGRO["FES-DataKnowledgeRepresentationLanguageWeakMetric"],
                FAIRAGRO["FES-DataKnowledgeRepresentationLanguageStrongMetric"],
                FAIRAGRO["FES-MetadataUsesFAIRVocabulariesWeakMetric"],
                FAIRAGRO["FES-MetadataUsesFAIRVocabulariesStrongMetric"],
                FAIRAGRO["FES-MetadataContainsQualifiedOutwardReferencesMetric"]
            ]
        },
        "reusability": {
            "dimension_uri": FAIRAGRO["reusability"],
            "definition": "The degree to which data can be reused for future research and analysis. This involves providing rich metadata, clear usage licenses, and provenance information to ensure data can be effectively reused.",
            "metrics": [
                FAIRAGRO["FES-MetadataIncludesLicenseStrongMetric"],
                FAIRAGRO["FES-MetadataIncludesLicenseWeakMetric"]
            ]
        }
    }
}

fuji_metric_mapping = {
    "FsF-F1-01D-1": FAIRAGRO["FsF-GloballyUniqueIdentifierMetric-1"],
    "FsF-F1-01D-2": FAIRAGRO["FsF-GloballyUniqueIdentifierMetric-2"],
    "FsF-F1-02D-1": FAIRAGRO["FsF-PersistentIdentifierMetric-1"],
    "FsF-F1-02D-2": FAIRAGRO["FsF-PersistentIdentifierMetric-2"],
    "FsF-F2-01M-1": FAIRAGRO["FsF-DescriptiveCoreMetadataMetric-1"],
    "FsF-F2-01M-2": FAIRAGRO["FsF-DescriptiveCoreMetadataMetric-2"],
    "FsF-F2-01M-3": FAIRAGRO["FsF-DescriptiveCoreMetadataMetric-3"],
    "FsF-F3-01M-1": FAIRAGRO["FsF-InclusionOfDataIdentifierInMetadataMetric-1"],
    "FsF-F3-01M-2": FAIRAGRO["FsF-InclusionOfDataIdentifierInMetadataMetric-2"],
    "FsF-F4-01M-1": FAIRAGRO["FsF-SearchableMetadataMetric-1"],
    "FsF-F4-01M-2": FAIRAGRO["FsF-SearchableMetadataMetric-2"],
    "FsF-A1-01M-1": FAIRAGRO["FsF-AccessConditionsMetric-1"],
    "FsF-A1-01M-2": FAIRAGRO["FsF-AccessConditionsMetric-2"],
    "FsF-A1-01M-3": FAIRAGRO["FsF-AccessConditionsMetric-3"],
    "FsF-A1-02M-1": FAIRAGRO["FsF-StandardCommunicationProtocolMetadataMetric-1"],
    "FsF-A1-03D-1": FAIRAGRO["FsF-StandardCommunicationProtocolDataMetric-1"],
    "FsF-I1-01M-1": FAIRAGRO["FsF-FormalMetadataRepresentationMetric-1"],
    "FsF-I1-01M-2": FAIRAGRO["FsF-FormalMetadataRepresentationMetric-2"],
    "FsF-I2-01M-1": FAIRAGRO["FsF-SemanticMetadataResourcesMetric-1"],
    "FsF-I2-01M-2": FAIRAGRO["FsF-SemanticMetadataResourcesMetric-2"],
    "FsF-I3-01M-1": FAIRAGRO["FsF-LinksToRelatedEntitiesMetric-1"],
    "FsF-I3-01M-2": FAIRAGRO["FsF-LinksToRelatedEntitiesMetric-2"],
    "FsF-R1-01MD-1": FAIRAGRO["FsF-ContentDescriptionMetric-1"],
    "FsF-R1-01MD-1a": FAIRAGRO["FsF-ContentDescriptionMetric-1a"],
    "FsF-R1-01MD-1b": FAIRAGRO["FsF-ContentDescriptionMetric-1b"],
    "FsF-R1-01MD-2": FAIRAGRO["FsF-ContentDescriptionMetric-2"],
    "FsF-R1-01MD-2a": FAIRAGRO["FsF-ContentDescriptionMetric-2a"],
    "FsF-R1-01MD-2b": FAIRAGRO["FsF-ContentDescriptionMetric-2b"],
    "FsF-R1-01MD-3": FAIRAGRO["FsF-ContentDescriptionMetric-3"],
    "FsF-R1-01MD-4": FAIRAGRO["FsF-ContentDescriptionMetric-4"],
    "FsF-R1.1-01M-1": FAIRAGRO["FsF-LicenseInformationMetric-1"],
    "FsF-R1.1-01M-2": FAIRAGRO["FsF-LicenseInformationMetric-2"],
    "FsF-R1.2-01M-1": FAIRAGRO["FsF-ProvenanceInformationMetric-1"],
    "FsF-R1.2-01M-2": FAIRAGRO["FsF-ProvenanceInformationMetric-2"],
    "FsF-R1.3-01M-1": FAIRAGRO["FsF-CommunityMetadataStandardMetric-1"],
    "FsF-R1.3-01M-2": FAIRAGRO["FsF-CommunityMetadataStandardMetric-2"],
    "FsF-R1.3-01M-3": FAIRAGRO["FsF-CommunityMetadataStandardMetric-3"],
    "FsF-R1.3-02D-1": FAIRAGRO["FsF-DataFileFormatMetric-1"],
    "FsF-R1.3-02D-1a": FAIRAGRO["FsF-DataFileFormatMetric-1a"],
    "FsF-R1.3-02D-1b": FAIRAGRO["FsF-DataFileFormatMetric-1b"],
    "FsF-R1.3-02D-1c": FAIRAGRO["FsF-DataFileFormatMetric-1c"]
}
