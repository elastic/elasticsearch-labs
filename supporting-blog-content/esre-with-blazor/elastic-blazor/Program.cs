using BlazorApp.Components;
using BlazorApp.Services;
using Elastic.Clients.Elasticsearch;
using Elastic.Transport;

var builder = WebApplication.CreateBuilder(args);

builder.Services.AddRazorComponents().AddInteractiveServerComponents();

builder.Services.AddScoped(sp =>
{
    var configuration = sp.GetRequiredService<IConfiguration>();
    var cloudId = configuration["ElasticsearchCloudId"];
    var apiKey = configuration["ElasticsearchApiKey"];

    if (string.IsNullOrEmpty(cloudId) || string.IsNullOrEmpty(apiKey))
    {
        throw new InvalidOperationException(
            "Elasticsearch credentials are missing in configuration."
        );
    }

    var settings = new ElasticsearchClientSettings(cloudId, new ApiKey(apiKey)).EnableDebugMode();
    return new ElasticsearchClient(settings);
});

builder.Services.AddScoped<ElasticsearchService>();

var app = builder.Build();

if (!app.Environment.IsDevelopment())
{
    app.UseExceptionHandler("/Error", createScopeForErrors: true);
    app.UseHsts();
}

app.UseHttpsRedirection();
app.UseStaticFiles();
app.UseAntiforgery();

app.MapRazorComponents<App>().AddInteractiveServerRenderMode();

app.Run();
