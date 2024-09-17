using BlazorApp.Models;
using Elastic.Clients.Elasticsearch;
using Elastic.Clients.Elasticsearch.QueryDsl;

namespace BlazorApp.Services
{
    public class ElasticsearchService
    {
        private readonly ElasticsearchClient _client;
        private readonly ILogger<ElasticsearchService> _logger;

        public ElasticsearchService(
            ElasticsearchClient client,
            ILogger<ElasticsearchService> logger
        )
        {
            _client = client ?? throw new ArgumentNullException(nameof(client));
            _logger = logger;
        }

        public Dictionary<string, Dictionary<string, long>> FormatFacets(
            Elastic.Clients.Elasticsearch.Aggregations.AggregateDictionary aggregations
        )
        {
            var facets = new Dictionary<string, Dictionary<string, long>>();

            foreach (var aggregation in aggregations)
            {
                if (
                    aggregation.Value
                    is Elastic.Clients.Elasticsearch.Aggregations.StringTermsAggregate termsAggregate
                )
                {
                    var facetName = aggregation.Key;
                    var facetDictionary = ConvertFacetDictionary(
                        termsAggregate.Buckets.ToDictionary(b => b.Key, b => b.DocCount)
                    );
                    facets[facetName] = facetDictionary;
                }
            }

            return facets;
        }

        private static Action<QueryDescriptor<BookDoc>> BuildSemanticQuery(
            string searchTerm,
            Dictionary<string, List<string>> selectedFacets
        )
        {
            var filters = new List<Action<QueryDescriptor<BookDoc>>>();

            if (selectedFacets != null)
            {
                foreach (var facet in selectedFacets)
                {
                    foreach (var value in facet.Value)
                    {
                        var field = facet.Key.ToLower();
                        if (!string.IsNullOrEmpty(field))
                        {
                            filters.Add(m => m.Term(t => t.Field(new Field(field)).Value(value)));
                        }
                    }
                }
            }

            return query =>
                query.Bool(b =>
                    b.Must(m => m.Semantic(sem => sem.Field("longDescription").Query(searchTerm)))
                        .Filter(filters.ToArray())
                );
        }

        private static Action<QueryDescriptor<BookDoc>> BuildMultiMatchQuery(
            string searchTerm,
            Dictionary<string, List<string>> selectedFacets
        )
        {
            var filters = new List<Action<QueryDescriptor<BookDoc>>>();

            if (selectedFacets != null)
            {
                foreach (var facet in selectedFacets)
                {
                    foreach (var value in facet.Value)
                    {
                        var field = facet.Key.ToLower();
                        if (!string.IsNullOrEmpty(field))
                        {
                            filters.Add(m => m.Term(t => t.Field(new Field(field)).Value(value)));
                        }
                    }
                }
            }

            if (string.IsNullOrEmpty(searchTerm))
            {
                return query => query.Bool(b => b.Filter(filters.ToArray()));
            }

            return query =>
                query.Bool(b =>
                    b.Should(m =>
                            m.MultiMatch(mm =>
                                mm.Query(searchTerm).Fields(new[] { "title", "shortDescription" })
                            )
                        )
                        .Filter(filters.ToArray())
                );
        }

        private static Action<RetrieverDescriptor<BookDoc>> BuildHybridQuery(
            string searchTerm,
            Dictionary<string, List<string>> selectedFacets
        )
        {
            var filters = new List<Action<QueryDescriptor<BookDoc>>>();

            if (selectedFacets != null)
            {
                foreach (var facet in selectedFacets)
                {
                    foreach (var value in facet.Value)
                    {
                        var field = facet.Key.ToLower();
                        if (!string.IsNullOrEmpty(field))
                        {
                            filters.Add(m => m.Term(t => t.Field(new Field(field)).Value(value)));
                        }
                    }
                }
            }

            return retrievers =>
                retrievers.Rrf(rrf =>
                    rrf.RankWindowSize(50)
                        .RankConstant(20)
                        .Retrievers(
                            retrievers =>
                                retrievers.Standard(std =>
                                    std.Query(q =>
                                        q.Bool(b =>
                                            b.Must(m =>
                                                    m.MultiMatch(mm =>
                                                        mm.Query(searchTerm)
                                                            .Fields(
                                                                new[]
                                                                {
                                                                    "title",
                                                                    "shortDescription",
                                                                }
                                                            )
                                                    )
                                                )
                                                .Filter(filters.ToArray())
                                        )
                                    )
                                ),
                            retrievers =>
                                retrievers.Standard(std =>
                                    std.Query(q =>
                                        q.Bool(b =>
                                            b.Must(m =>
                                                    m.Semantic(sem =>
                                                        sem.Field("longDescription")
                                                            .Query(searchTerm)
                                                    )
                                                )
                                                .Filter(filters.ToArray())
                                        )
                                    )
                                )
                        )
                );
        }

        public async Task<ElasticResponse> SearchBooksAsync(
            string searchTerm,
            Dictionary<string, List<string>> selectedFacets
        )
        {
            try
            {
                _logger.LogInformation($"Performing search for: {searchTerm}");

                var retrieverQuery = BuildHybridQuery(searchTerm, selectedFacets);
                var multiMatchQuery = BuildMultiMatchQuery(searchTerm, selectedFacets);
                var semanticQuery = BuildSemanticQuery(searchTerm, selectedFacets);

                /**
                 * * MultiMatch Search
                 */
                // var response = await _client.SearchAsync<BookDoc>(s =>
                //     s.Index("elastic-blazor-books")
                //         .Query(multiMatchQuery)
                //         .Aggregations(aggs =>
                //             aggs.Add("Authors", agg => agg.Terms(t => t.Field(p => p.Authors)))
                //                 .Add(
                //                     "Categories",
                //                     agg => agg.Terms(t => t.Field(p => p.Categories))
                //                 )
                //                 .Add("Status", agg => agg.Terms(t => t.Field(p => p.Status)))
                //         )
                // );

                /**
                 * * Semantic Search
                 */
                // var response = await _client.SearchAsync<BookDoc>(s =>
                //     s.Index("elastic-blazor-books")
                //         .Query(semanticQuery)
                //         .Aggregations(aggs =>
                //             aggs.Add("Authors", agg => agg.Terms(t => t.Field(p => p.Authors)))
                //                 .Add(
                //                     "Categories",
                //                     agg => agg.Terms(t => t.Field(p => p.Categories))
                //                 )
                //                 .Add("Status", agg => agg.Terms(t => t.Field(p => p.Status)))
                //         )
                // );

                /**
                 * * Hybrid Search
                 */
                var response = await _client.SearchAsync<BookDoc>(s =>
                    s.Index("elastic-blazor-books")
                        .Retriever(retrieverQuery)
                        .Aggregations(aggs =>
                            aggs.Add("Authors", agg => agg.Terms(t => t.Field(p => p.Authors)))
                                .Add(
                                    "Categories",
                                    agg => agg.Terms(t => t.Field(p => p.Categories))
                                )
                                .Add("Status", agg => agg.Terms(t => t.Field(p => p.Status)))
                        )
                );

                if (response.IsValidResponse)
                {
                    _logger.LogInformation($"Found {response.Documents.Count} documents");

                    var hits = response.Total;
                    var facets =
                        response.Aggregations != null
                            ? FormatFacets(response.Aggregations)
                            : new Dictionary<string, Dictionary<string, long>>();

                    var elasticResponse = new ElasticResponse
                    {
                        TotalHits = hits,
                        Documents = response.Documents.ToList(),
                        Facets = facets,
                    };

                    return elasticResponse;
                }
                else
                {
                    _logger.LogWarning($"Invalid response: {response.DebugInformation}");
                    return new ElasticResponse();
                }
            }
            catch (Exception ex)
            {
                _logger.LogError(ex, "Error performing search");
                return new ElasticResponse();
            }
        }

        private Dictionary<string, long> ConvertFacetDictionary(
            Dictionary<Elastic.Clients.Elasticsearch.FieldValue, long> original
        )
        {
            var result = new Dictionary<string, long>();
            foreach (var kvp in original)
            {
                result[kvp.Key.ToString()] = kvp.Value;
            }
            return result;
        }
    }
}
