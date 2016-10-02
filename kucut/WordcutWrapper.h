#include <iostream>
#include<boost/python.hpp>
#include<sys/stat.h>

using namespace std;
using namespace boost::python;

class Wordcut {

private:
// Private : Attribute
	std::string lexicon_file;
	std::string syllable_file;
	std::string corpus_db;
    
// Private : Method
    char *readPythonScript(const char* fileName);
    
public:
// Constructor
    Wordcut(std::string, std::string, std::string);
    
// Public : Method
	std::string cut(char*, char*);
};
            
