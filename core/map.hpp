#ifndef MAP_HPP
#define MAP_HPP

#include <stdio.h>

template <typename K, typename V>
class MapEntry {
public:
    K _k;
    V _v;
    
    MapEntry(const MapEntry<K, V>& entry);
    MapEntry(K k, V v) : _k(k), _v(v) {}
    MapEntry() : _k(0), _v(0) {}
};

template <typename K, typename V>
class Map {
private:
    MapEntry<K, V>* _entries;
    int _size;
    int _length;
    
    void expand();
public:
    Map();

    int  size() { return _size; }
    void put(K k, V v);
    V    get(K k);
    K    get_key(int index);
    V    remove(K k);
    int  index(K k);
    MapEntry<K, V>* entries() { return _entries; }
};

#endif