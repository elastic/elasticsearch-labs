namespace BlazorApp.Models
{
    public class ElasticResponse
    {
        public ElasticResponse()
        {
            Documents = new List<BookDoc>();
            Facets = new Dictionary<string, Dictionary<string, long>>();
        }

        public long TotalHits { get; set; }
        public List<BookDoc> Documents { get; set; }
        public Dictionary<string, Dictionary<string, long>> Facets { get; set; }
    }
}
