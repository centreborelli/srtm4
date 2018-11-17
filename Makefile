C99 = $(CC) -std=c99
CFLAGS = -g -O3 -DNDEBUG -DDONT_USE_TEST_MAIN
CPPFLAGS = -g -O3 -fpermissive -DNDEBUG -DDONT_USE_TEST_MAIN
LDLIBS = -lstdc++ -lz -lm -ltiff

default: bin bin/srtm4 bin/srtm4_which_tile

src/Geoid.o: src/Geoid.cpp
	$(CXX) $(CPPFLAGS) -c $^ -o $@

src/geoid_height_wrapper.o: src/geoid_height_wrapper.cpp
	$(CXX) $(CPPFLAGS) -c $^ -o $@

bin/srtm4: src/srtm4.c src/Geoid.o src/geoid_height_wrapper.o
	$(C99) $(CFLAGS) -DMAIN_SRTM4 $^ $(LDLIBS) -o $@

bin/srtm4_which_tile: src/srtm4.c src/Geoid.o src/geoid_height_wrapper.o
	$(C99) $(CFLAGS) -DMAIN_SRTM4_WHICH_TILE $^ $(LDLIBS) -o $@

bin:
	mkdir -p bin

clean:
	-rm -f -r bin
	-rm -f src/*.o
