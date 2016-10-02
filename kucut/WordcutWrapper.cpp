#include "WordcutWrapper.h"

Wordcut::Wordcut(std::string lf, std::string sf, std::string c_db)
{
    lexicon_file = lf;
    syllable_file = sf;
    corpus_db = c_db;
}

std::string Wordcut::cut(char* sentence, char* mode)
{
    char *pythonScript;

	Py_Initialize();
	handle<>main_module(borrowed(PyImport_AddModule("__main__")));
	dict main_namespace(borrowed(PyModule_GetDict(main_module.get())));

    pythonScript = readPythonScript("wordcut.py");

    char* defDictionary = new char[256];
    sprintf(defDictionary,
        "\nlexiconDict = Dictionary('%s')\n"
        "syllableDict = Dictionary('%s')\n"
        "strOut = ''\n",
        lexicon_file.c_str(),syllable_file.c_str());

    char* callCutting = new char[512];
    sprintf(callCutting,
        "seg = Segmentation('%s',syllable=syllableDict,"
		"lexicon=lexiconDict,"
		"debug=False,"
        "quiet=True,"
		"database='%s',"
		"mode='%s')\n"
        "seg.input_file = '%s'\n"
		"seg.loadProhibitPattern('%s')\n"
        "results,ambiguous_list = seg.tokenize(['%s'],style='Normal',space=0)\n"        
        ,"test.txt",corpus_db.c_str(),mode,"test.txt","dict/prohibit.txt",sentence);

	cout << strlen(defDictionary) << endl;
	cout << strlen(callCutting) << endl;

    char displayResult[] = "for result in results:\n"
                            "\tfor t in result[1]:\n"
                            "\t\tfor r in t[0]:\n"
                            "\t\t\tstrOut += r + ' '\n"
                            "\t\tstrOut += '\\n'\n";


    char* cmd;
	cmd = new char[strlen(pythonScript)+strlen(defDictionary)+strlen(callCutting)+strlen(displayResult)+1];

    sprintf(cmd,"%s%s%s%s",pythonScript,defDictionary,callCutting,displayResult);

	cout << strlen(cmd) << endl;
	
	handle<>result(allow_null( PyRun_String(cmd, Py_file_input, main_namespace.ptr(), main_namespace.ptr())) );

	std::string output;
	if (result) {
		output = extract<std::string>( main_namespace["strOut"] );
	}
    Py_Finalize();

	delete [] callCutting;
	delete [] defDictionary;
	delete [] cmd;
    
    return output;
}

char* Wordcut::readPythonScript(const char* fileName)
{
    FILE *pFile = fopen(fileName, "r");
    if(pFile == NULL) {
        return 0;
    }
    struct stat fileStats;

    if(stat(fileName, &fileStats) != 0) {
        return 0;
    }

    char *buffer = new char[fileStats.st_size];
    int bytes = fread( buffer,1,fileStats.st_size,pFile);
    buffer[bytes] = 0;
    fclose(pFile);

    return buffer;

}

/************* Main Test *************/ 
int main()
{
    Wordcut wc("dict/lexicon.txt","dict/syllable.txt","corpus.db");
    cout << wc.cut("ฉันกินข้าวที่บ้านดอกไม้","syllable") << endl;
    return 0;
}
/*************************************/
