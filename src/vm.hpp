#include <string>
#include <exception>
#include <stack>
#include <memory>

class VMException: public std::exception {
    public:
        VMException(const std::string &msg) : errMsg_(msg) {
            const char* what() const noexcept {
                return errMsg_.c_str();
            }
        }
    private:
        std::string errMsg_;
}

class vm {
    
}