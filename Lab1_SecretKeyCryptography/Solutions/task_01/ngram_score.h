#ifndef NGRAM_SCORE_H
#define NGRAM_SCORE_H

#include<map>
#include<string>

/**
 * ngram_score class to build up a lookup database and
 * provide scoring function to score texts based on
 * n-gram statistics. The database used for the calculations
 * have to be provided during object initialization by means
 * of a simple text-file containing line by line the n-gramms
 * and there correspondnig occurency in the specific language.
 * The implementation omits any defensive programming techniques,
 * i.e., the user / developer have to take care of proper
 * input and/or output formats.
 * 
 * Author:  Torsten Ziemann
 * Date:    11.10.2021
 */
class ngram_score
{
    public:
        /**
         * Constructs a new ngram_score object from the
         * ngram_file providing the list of n-grams and
         * there related occurencies.
         */
        ngram_score(const std::string& ngram_file);

        /**
         * Return the Order of n-gramms, i.e., n,
         * used as the backend for the scoring
         * function.
         */
        inline const int get_order() const {  return gram_order; }

        /**
         * Calculate the Score of the input text based on
         * the lookup table.
         */
        const float get_score(const std::string& text, const bool normalize = false) const;


    private:
        int                             gram_order;             // Order, i.e., n
        float                           default_propability;    // propability assigned to n-grams not contained in the loopup-table
        std::map<const std::string, float>    n_gramms;               // look-up table 
};

#endif
