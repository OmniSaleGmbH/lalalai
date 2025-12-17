#include <iostream>
#include <fstream>
#include <sstream>
#include <string>
#include <curl/curl.h>

size_t WriteCallback(char *contents, size_t size, size_t nmemb, void *userp)
{
    ((std::string *)userp)->append((char *)contents, size * nmemb);
    return size * nmemb;
}

void uploadData(std::string data)
{
    CURL *curl;
    CURLcode res;

    curl_global_init(CURL_GLOBAL_DEFAULT);
    curl = curl_easy_init();

    if (curl)
    {
        curl_easy_setopt(curl, CURLOPT_URL, "https://www.lalal.ai/api/upload/");
        curl_easy_setopt(curl, CURLOPT_POST, 1L);

        struct curl_slist *list = NULL;
        list = curl_slist_append(list, "Content-Disposition: attachment; filename=file.mp3");
        list = curl_slist_append(list, "Authorization: license <PASTE LICENSE HERE>"); // TODO: PASTE LICENSE HERE
        curl_easy_setopt(curl, CURLOPT_HTTPHEADER, list);

        curl_easy_setopt(curl, CURLOPT_POSTFIELDSIZE, data.size());
        curl_easy_setopt(curl, CURLOPT_POSTFIELDS, data.c_str());

        std::string readBuffer;
        curl_easy_setopt(curl, CURLOPT_WRITEFUNCTION, WriteCallback);
        curl_easy_setopt(curl, CURLOPT_WRITEDATA, &readBuffer);

        res = curl_easy_perform(curl);

        std::cout << "[" << readBuffer << "]" << std::endl;

        if (res != CURLE_OK)
            fprintf(stderr, "curl_easy_perform() failed: %s\n", curl_easy_strerror(res));

        curl_easy_cleanup(curl);
        curl_slist_free_all(list);
    }

    curl_global_cleanup();
}

int main()
{
    const std::string fileName = "~/file.mp3"; // TODO: PASTE FILENAME HERE

    std::ifstream inFile;
    inFile.open(fileName, std::ios::binary);

    if (!inFile)
    {
        std::cerr << "Error: Unable to open file " << fileName << std::endl;
        return 1;
    }

    std::stringstream strStream;
    strStream << inFile.rdbuf();
    auto str = strStream.str();

    try
    {
        uploadData(std::move(str));
    }
    catch (const std::exception &e)
    {
        std::cerr << "Error: " << e.what() << '\n';
    }

    return 0;
}
