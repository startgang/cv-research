/**
 * libdmtx - Data Matrix Encoding/Decoding Library
 * Copyright 2008, 2009 Mike Laughton. All rights reserved.
 * Copyright 2010-2016 Vadim A. Misbakh-Soloviov. All rights reserved.
 * Copyright 2016 Tim Zaman. All rights reserved.
 *
 * See LICENSE file in the main project directory for full
 * terms of use and distribution.
 *
 * Contact:
 * Vadim A. Misbakh-Soloviov <dmtx@mva.name>
 * Mike Laughton <mike@dragonflylogic.com>
 *
 * \file simple_test.c
 */

#include <opencv2/opencv.hpp>
#include <opencv2/imgproc.hpp>

#include <string>
#include <chrono>
#include <iostream>

#include <stdlib.h>
#include <stdio.h>
#include <string.h>
#include <assert.h>
#include <math.h>
#include <dmtx.h>

cv::Mat resizeImage(const cv::Mat& input, int max_dimension = 240) {
    cv::Mat output;
    int max_dim = std::max(input.cols, input.rows);
    
    if (max_dim > max_dimension) {
        double scale = (double)max_dimension / max_dim;
        cv::resize(input, output, cv::Size(), scale, scale, cv::INTER_LINEAR);
        return output;
    }
    return input.clone();
}

int
main(int argc, char *argv[])
{
	DmtxImage		*img;
	DmtxDecode	  *dec;
	DmtxRegion	  *reg;
	DmtxMessage	 *msg;

	// Load real image

	auto dm_filename = std::string("../dm1.jpg");

	cv::Mat bgr_img = cv::imread(dm_filename, cv::IMREAD_COLOR);
	assert(!bgr_img.empty());

	cv::Mat rgb_img;
    cv::cvtColor(bgr_img, rgb_img, cv::COLOR_BGR2RGB);

    rgb_img = resizeImage(rgb_img);

    img = dmtxImageCreate(
        rgb_img.data,      // pointer to image data
        rgb_img.cols,      // width
        rgb_img.rows,      // height
        DmtxPack24bppRGB   // pixel format (RGB 24-bit)
    );

	assert(img != NULL);

	auto start = std::chrono::high_resolution_clock::now();
    dec = dmtxDecodeCreate(img, 1);
	assert(dec != NULL);

    dmtxDecodeSetProp(dec, DmtxPropEdgeMin, 100);    // Very high threshold (fast)
    dmtxDecodeSetProp(dec, DmtxPropEdgeMax, 200);    // Narrow range
    dmtxDecodeSetProp(dec, DmtxPropScanGap, 4);      // Fast scanning
    auto end = std::chrono::high_resolution_clock::now();
    
	reg = dmtxRegionFindNext(dec, NULL);

    auto duration = std::chrono::duration_cast<std::chrono::microseconds>(end - start);
	if(reg != NULL) {
		msg = dmtxDecodeMatrixRegion(dec, reg, DmtxSchemeAscii);
        auto end = std::chrono::high_resolution_clock::now();

        duration = std::chrono::duration_cast<std::chrono::microseconds>(end - start);

		fprintf(stdout, "msg->arraySize :  \"%zd\"\n", msg->arraySize );
		fprintf(stdout, "msg->codeSize  :  \"%zd\"\n", msg->codeSize  );
		fprintf(stdout, "msg->outputSize:  \"%zd\"\n", msg->outputSize);
		int oned = sqrt(msg->arraySize);
		for (int i=0; i<msg->arraySize; i++){
			fprintf(stdout, " %c.", msg->array[i]);
			if (i%oned==oned-1){
				fprintf(stdout, "\n");
			}
		}
		fprintf(stdout, "\n\n");
		for (int j=0; j<msg->codeSize; j++){
			fprintf(stdout, " %c.", msg->code[j]);
		}
		fprintf(stdout, "\n\n");
		for (int k=0; k<msg->outputSize; k++){
			fprintf(stdout, " %c.", msg->output[k]);
		}
		fprintf(stdout, "\n\n");

		if(msg != NULL) {
			fputs("output: \"", stdout);
			fwrite(msg->output, sizeof(unsigned char), msg->outputIdx, stdout);
			fputs("\"\n", stdout);
			dmtxMessageDestroy(&msg);
		}
		dmtxRegionDestroy(&reg);
	} else {
        std::cout << "Not found" << std::endl;
    }

	dmtxDecodeDestroy(&dec);
	dmtxImageDestroy(&img);
	//free(pxl);

	fprintf(stdout, "%d\n", getSizeIdxFromSymbolDimension(12, 12));

            std::cout << "Time, µs: " << duration.count() << std::endl;
        
	exit(0);
}
