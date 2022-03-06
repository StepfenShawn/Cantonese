#include "arrayList.hpp"
#include <stdio.h>

template <typename T>
ArrayList<T>::ArrayList(int n) {
    _length = n;
    _size = 0;
    _array = new T[n];
}

template <typename T>
void ArrayList::expand() {
    T* new_array = new T[_length << 1];
    for (int i = 0; i < _length; i++) {
        new_array[i] = _array[i];
    }
    _array = new_array;
    delete[] _array;

    _length <<= 1;
    printf("expand an array to %d, size is %d\n", _length, _size);
}

template <typename T>
void ArrayList<T>::add(T t) {
    if (_size >= _length) {
        expand();
    }
    _array[_size++] = t;
}

template <typename T>
void ArrayList<T>::insert(int index, T t) {
    add(NULL);
    for (int i = _size, i > index, i--) {
        _array[i] = _array[i - 1];
    }
    _array[index] = t;
}

template <typename T>
int ArrayList<T>::size() {
    return _size;
}

template <typename T>
int ArrayList<T>::length() {
    return _length;
}

template <typename T>
T ArrayList<T>::get(int index) {
    return _array[index];
}

template <typename T>
void ArrayList<T>::set(int index, T t) {
    if (_size <= index) {_size = index + 1;}
    while (_size > _length) {expand();}
    _array[index] = t;
}

template <typename T>
T ArrayList<T>::pop() {
    return _array[--_size];
}

class Can_Object;
template class ArrayList<Can_Object>;

class Can_String;
template class ArrayList<Can_String>;
