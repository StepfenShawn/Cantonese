#include <iostream>
#include <fstream>
#include <sstream>
#include <string>
#include "lexer.hpp"

using namespace cantonese;
using namespace std;


void args_parse(std::string str);
void _help();
std::wstring readFile(std::string filename);

enum msg
{
    help,
    version,
    default_
};

std::wstring readFile(std::string filename) {
   ifstream ifile(filename, ios::binary);
   wstring res;
   if (ifile) {
		wchar_t wc;
		while (!ifile.eof()) {
			ifile.read((char *)(&wc), 2);
			res = res + wc;
		}
	}
	ifile.close();
	return res;
}

void args_parse(std::string str) {
    msg temp = default_;
    if (str == "-h" || str == "-H" || str == "-help") {temp = help;}
    if (str == "-v" || str == "-V" || str == "-version") {temp = version;}
    switch (temp)
    {
    case help:
        _help();
        break;
    case version:
        std::cout<<"Cantonese (Core) version 1.0.0"<<std::endl;
        break;
    default:
        std::string filename = str;
        std::wstring code;
        code = readFile(filename);
        wchar_t *wcht = new wchar_t[code.size() + 1];
        wcht[code.size()] = 0;
        std::copy(code.begin(), code.end(), wcht);
        std::wcout<<code<<std::endl;
        auto *source = const_cast<CAN_Char *>(wcht);
        cantonese::Lexer lexer(source);
        do
        {
            lexer.Read().dump(wcout);
        } while (lexer.Read().mType != TokenType::End);
        break;
    }
}

void _help() {
    std::string info = "usage:\n -h   : use help \n -v   : print the version\n -e   : exec a statement ";
    std::cout<<info<<std::endl;
}

int main(int argc, char* argv[]) {
    /* Only for mingw */
    /* TODO: test under VS */
    std::setlocale(LC_ALL, "");
    std::ios_base::sync_with_stdio(false);

    for (int i = 0; i < argc; i++) {
        if (i != 0) {args_parse(argv[i]);}
    }

    auto *source = const_cast<CAN_Char *>(_CAN_C("收工"));
    cantonese::Lexer lexer(source);
    do
    {
        lexer.Read().dump(wcout);
    } while (lexer.Read().mType != TokenType::End);
    return 0;
}