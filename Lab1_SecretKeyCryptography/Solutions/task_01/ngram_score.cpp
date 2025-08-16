#include "ngram_score.h"

#include<iostream>
#include<fstream>
#include<cmath>
#include<algorithm>
#include<numeric>


/**
 * Constructs a new ngram_score object from the
 * ngram_file providing the list of n-grams and
 * there related occurencies.
 */
ngram_score::ngram_score(const std::string& ngram_file)
    : gram_order(-1), default_propability(0.0f)
{
    // read in the n-gramms from file to STL map and count
    // the total number of read in data for normalization
    std::ifstream file(ngram_file.c_str());
    std::string key;
    float value = 0.0f;
    size_t total_num_ngrams = 0;
    while(file >> key >> value)
    {
        n_gramms[key] = value;
        total_num_ngrams += value;
        
    }

    // fix some internal parameters
    // I.e., order of the read n-gramms, total number read entities
    gram_order = n_gramms.empty() ? 0 : n_gramms.begin()->first.length();

    // normalize occurencies to log scale propability
    for(std::map<const std::string, float>::iterator iter = n_gramms.begin(); 
        iter != n_gramms.end(); ++iter)
    {
        iter->second = std::log10(iter->second / total_num_ngrams);
    }

    // Set default value for all n-grams may later processed by get_score()
    // which are not in our look-up table
    default_propability = std::log10(0.01f / static_cast<float>(total_num_ngrams));
}


 /**
   * Calculate the Score of the input text based on
   * the lookup table.
   */
const float ngram_score::get_score(const std::string& input_text, const bool normalize) const
{
    // transform input string to upper case
    std::string text(input_text);
    std::transform(text.begin(), text.end(),text.begin(), ::toupper);
    std::cout << text << std::endl;
    float score = 0.0f;
    const size_t num_grams = text.length() - gram_order + 1;
    for(size_t ix = 0; ix != num_grams; ++ix)
    {
        const std::string current_gram = text.substr(ix, ix + gram_order);
        if( n_gramms.find(current_gram) != n_gramms.end() )
        {
            score += n_gramms.at(current_gram);
        }
        else 
        {
            score += default_propability;
        }
    }

    // normalize the score to the length of the
    // given input text. Otherwise longer texts
    // will automatically have lower score, even
    // if they were better natural language
    if(normalize)
    {
        score /= (text.length() - gram_order + 1);
    }

    return score;
}
