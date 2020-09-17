ORIGINAL_DIR="original"
mkdir $ORIGINAL_DIR
wget https://vitessce-data.s3.amazonaws.com/source-data/spraggins/spraggins.ome.tif -O ${ORIGINAL_DIR}/spraggins.ome.tif

DERIVED_DIR="derived"
mkdir $DERIVED_DIR
cd $DERIVED_DIR
tile_sizes=(256 512 1024)
for tile_size in "${tile_sizes[@]}"
do
  ZARR_NAME="spraggins_${tile_size}"
	bioformats2raw ../${ORIGINAL_DIR}/spraggins.ome.tif $ZARR_NAME --file_type=zarr --tile_height $tile_size --tile_width $tile_size
  aws s3 cp --recursive $ZARR_NAME s3://viv-benchmark/data
  bioformats2raw spraggins.ome.tif spraggins.n5/ --tile_height $tile_size --tile_width $tile_size
  compression_algos=("zlib" "lzw")
  for algo in "${compression_algos[@]}"
  do
    TIFF_NAME="spraggins_${tile_size}_${algo}.ome.tif"
    raw2ometiff spraggins.n5/ $TIFF_NAME --compression=$algo
    aws s3 cp $TIFF_NAME s3://viv-benchmark/data
    rm $TIFF_NAME
  done
done
