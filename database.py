from annoy import AnnoyIndex

class DocumentDatabase:
    def __init__(self):
        self.documents = []
        self.segment_index = 0
        self.vectors = AnnoyIndex(1536, "angular")

    def __generate_index(self):
        return len(self.documents)

    def add_document(self, segments_embeddings):
        print("Adding document to database")
        document_segments = []

        for segment_embedding in segments_embeddings:
            print(segment_embedding['text'])
            document_segments.append({
                "id": self.segment_index,
                "text": segment_embedding['text']
            })
            self.vectors.add_item(self.segment_index, segment_embedding['embedding'])
            self.segment_index += 1

        self.documents.append({
            "id": self.__generate_index(),
            "segments": document_segments
        })

        self.vectors.build(10)

        print(self.documents)

        return self.vectors

    def find_relevant_documents(self, query_embedding, num_results = 5):
        ids = self.vectors.get_nns_by_vector(query_embedding, num_results)
        return [self.find_segment_by_id(i) for i in ids]


    def find_segment_by_id(self, segment_id):
        for document in self.documents:
            for segment in document["segments"]:
                print(segment, flush=True)
                if segment["id"] == segment_id:
                    return segment
        return None

    def get_document_ids(self, segment_ids):
        document_ids = []

        for segment_id in segment_ids:
            for document in self.documents:
                for segment in document["segments"]:
                    if segment["id"] == segment_id:
                        return document["id"]

        # Only return unique document ids
        return list(set(document_ids))