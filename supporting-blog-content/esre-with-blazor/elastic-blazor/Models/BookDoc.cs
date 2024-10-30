namespace BlazorApp.Models
{
    public class BookDoc
    {
        public string? Title { get; set; }
        public int? PageCount { get; set; }
        public string? PublishedDate { get; set; }
        public string? ThumbnailUrl { get; set; }
        public string? ShortDescription { get; set; }
        public LongDescription? LongDescription { get; set; }
        public string? Status { get; set; }
        public List<string>? Authors { get; set; }
        public List<string>? Categories { get; set; }
    }

    public class LongDescription
    {
        public string? Text { get; set; }
    }
}
