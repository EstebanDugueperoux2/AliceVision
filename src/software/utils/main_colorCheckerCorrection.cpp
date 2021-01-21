// This file is part of the AliceVision project.
// Copyright (c) 2021 AliceVision contributors.
// This Source Code Form is subject to the terms of the Mozilla Public License,
// v. 2.0. If a copy of the MPL was not distributed with this file,
// You can obtain one at https://mozilla.org/MPL/2.0/.

#include <aliceVision/image/all.hpp>
#include <aliceVision/sfmData/SfMData.hpp>
#include <aliceVision/sfmDataIO/sfmDataIO.hpp>
#include <aliceVision/sfmDataIO/viewIO.hpp>
#include <aliceVision/utils/regexFilter.hpp>
#include <aliceVision/utils/filesIO.hpp>

#include <aliceVision/system/cmdline.hpp>
#include <aliceVision/system/main.hpp>
#include <aliceVision/config.hpp>

#include <boost/filesystem.hpp>
#include <boost/program_options.hpp>

#include <opencv2/core.hpp>
#include <opencv2/imgproc/imgproc.hpp>
#include <opencv2/imgcodecs.hpp>
#include <opencv2/mcc.hpp>

#include <string>
#include <fstream>
#include <vector>
#include <unordered_map>

// These constants define the current software version.
// They must be updated when the command line is changed.
#define ALICEVISION_SOFTWARE_VERSION_MAJOR 1
#define ALICEVISION_SOFTWARE_VERSION_MINOR 0

using namespace aliceVision;

namespace fs = boost::filesystem;
namespace po = boost::program_options;

std::string type2str(int type)
{
    std::string r;

    uchar depth = type & CV_MAT_DEPTH_MASK;
    uchar chans = 1 + (type >> CV_CN_SHIFT);

    switch(depth)
    {
        case CV_8U:
            r = "8U";
            break;
        case CV_8S:
            r = "8S";
            break;
        case CV_16U:
            r = "16U";
            break;
        case CV_16S:
            r = "16S";
            break;
        case CV_32S:
            r = "32S";
            break;
        case CV_32F:
            r = "32F";
            break;
        case CV_64F:
            r = "64F";
            break;
        default:
            r = "User";
            break;
    }

    r += "C";
    r += (chans + '0');

    return r;
}

cv::Mat deserializeColorDataFromTextFile(const std::string &colorData) {
    int rows = 24;
    int cols = 1;
    cv::Mat out = cv::Mat::zeros(rows, cols, CV_64FC3); // Matrix to store values

    int i = 0;
    std::ifstream colorDataInputFile(colorData);

    for(std::string line; getline(colorDataInputFile, line);)
    {
        cv::Vec3d* rowPtr = out.ptr<cv::Vec3d>(i / 3);
        cv::Vec3d& matPixel = rowPtr[0];
        matPixel[i%3] = std::stod(line);
        ++i;
    }

    return out;
}

namespace tmp
{
    void cvMatBGRToImageRGBA(cv::Mat& img, image::Image<image::RGBAfColor>& imageOut)
    {
       for(int row = 0; row < imageOut.Height(); row++)
        {
            cv::Vec3b* rowPtr = img.ptr<cv::Vec3b>(row);
            for(int col = 0; col < imageOut.Width(); col++)
            {
                cv::Vec3b& matPixel = rowPtr[col];
                imageOut(row, col) = image::RGBAfColor(matPixel[2] / 255.f, matPixel[1] / 255.f, matPixel[0] / 255.f,
                                                       imageOut(row, col).a());
            }
       }
    }
} //tmp

void processColorCorrection(image::Image<image::RGBAfColor>& image, cv::Mat& refColors)
{
    cv::Mat imageBGR = image::imageRGBAToCvMatBGR(image, CV_8UC3);

    if(imageBGR.cols == 0 || imageBGR.rows == 0)
    {
        ALICEVISION_LOG_ERROR("Image is empty.");
        exit(EXIT_FAILURE);
    }

    cv::ccm::ColorCorrectionModel model(refColors, cv::ccm::COLORCHECKER_Macbeth);
    model.run();
    
    // set color space
    model.setColorSpace(cv::ccm::COLOR_SPACE_sRGB); // linear color spaces are not supported
    
    cv::Mat img;
    cvtColor(imageBGR, img, cv::COLOR_BGR2RGB);
    img.convertTo(img, CV_64F); // convert to 64 bits double matrix / image
    const int inpSize = 255;
    const int outSize = 255;
    img /= inpSize;
    cv::Mat calibratedImage = model.infer(img); // make correction using ccm matrix
    cv::Mat out = calibratedImage * outSize;

    calibratedImage.convertTo(calibratedImage, CV_8UC3, 255); // convert to 8 bits unsigned integer matrix / image with 3 channels
    cv::Mat imgOut = min(max(calibratedImage, 0), outSize);
    cv::Mat outImg;
    cvtColor(imgOut, outImg, cv::COLOR_RGB2BGR);

    tmp::cvMatBGRToImageRGBA(outImg, image);
}

int aliceVision_main(int argc, char** argv)
{
    // command-line parameters
    std::string verboseLevel = system::EVerboseLevel_enumToString(system::Logger::getDefaultVerboseLevel());
    std::string inputExpression;
    std::string inputColorData;
    std::string outputExtension;
    std::string outputPath;

    po::options_description allParams(
        "This program is used to perform color correction based on a color checker\n"
        "AliceVision colorCheckerCorrection");

    po::options_description requiredParams("Required parameters");
    requiredParams.add_options()
        ("input,i", po::value<std::string>(&inputExpression)->default_value(inputExpression),
        "SfMData file input, image filenames or regex(es) on the image file path (supported regex: '#' matches a "
        "single digit, '@' one or more digits, '?' one character and '*' zero or more).")(
        "inputColorData", po::value<std::string>(&inputColorData)->default_value(inputColorData),
        "Colorimetric data extracted from a detected color checker in the images")
        ("output,o", po::value<std::string>(&outputPath)->required(),
         "Output folder.")
        ;

    po::options_description optionalParams("Optional parameters");
    optionalParams.add_options()
        ("extension", po::value<std::string>(&outputExtension)->default_value(outputExtension),
         "Output image extension (like exr, or empty to keep the source file format.");

    po::options_description logParams("Log parameters");
    logParams.add_options()
        ("verboseLevel,v", po::value<std::string>(&verboseLevel)->default_value(verboseLevel),
         "verbosity level (fatal, error, warning, info, debug, trace).")
        ;

    allParams.add(requiredParams).add(optionalParams).add(logParams);

    po::variables_map vm;
    try
    {
        po::store(po::parse_command_line(argc, argv, allParams), vm);

        if(vm.count("help") || (argc == 1))
        {
            ALICEVISION_COUT(allParams);
            return EXIT_SUCCESS;
        }
        po::notify(vm);
    }
    catch(boost::program_options::required_option& e)
    {
        ALICEVISION_CERR("ERROR: " << e.what());
        ALICEVISION_COUT("Usage:\n\n" << allParams);
        return EXIT_FAILURE;
    }
    catch(boost::program_options::error& e)
    {
        ALICEVISION_CERR("ERROR: " << e.what());
        ALICEVISION_COUT("Usage:\n\n" << allParams);
        return EXIT_FAILURE;
    }

    ALICEVISION_COUT("Program called with the following parameters:");
    ALICEVISION_COUT(vm);

    // set verbose level
    system::Logger::get()->setLogLevel(verboseLevel);

    // check user choose an input
    if(inputExpression.empty())
    {
        ALICEVISION_LOG_ERROR("Program need --input option." << std::endl << "No input images here.");

        return EXIT_FAILURE;
    }

    // Get color data matrix from text file input 
    cv::Mat colorData = deserializeColorDataFromTextFile(inputColorData);

    // Map used to store paths of the views that need to be processed
    std::unordered_map<IndexT, std::string> ViewPaths;

    // Check if sfmInputDataFilename exist and is recognized as sfm data file
    const std::string inputExt = boost::to_lower_copy(fs::path(inputExpression).extension().string());
    static const std::array<std::string, 3> sfmSupportedExtensions = {".sfm", ".json", ".abc"};
    if(!inputExpression.empty() && std::find(sfmSupportedExtensions.begin(), sfmSupportedExtensions.end(), inputExt) !=
                                       sfmSupportedExtensions.end())
    {
        sfmData::SfMData sfmData;
        if(!sfmDataIO::Load(sfmData, inputExpression, sfmDataIO::VIEWS))
        {
            ALICEVISION_LOG_ERROR("The input SfMData file '" << inputExpression << "' cannot be read.");
            return EXIT_FAILURE;
        }

        // Map used to store paths of the views that need to be processed
        std::unordered_map<IndexT, std::string> ViewPaths;

        // Iterate over all views
        for(const auto& viewIt : sfmData.getViews())
        {
            const sfmData::View& view = *(viewIt.second);

            ViewPaths.insert({view.getViewId(), view.getImagePath()});
        }

        const int size = ViewPaths.size();
        int i = 0;

        for(auto& viewIt : ViewPaths)
        {
            const IndexT viewId = viewIt.first;
            const std::string viewPath = viewIt.second;
            sfmData::View& view = sfmData.getView(viewId);

            ALICEVISION_LOG_INFO(++i << "/" << size << " - Process view '" << viewId << "' for color correction.");

            // Read image options and load image
            image::ImageReadOptions options;
            options.outputColorSpace = image::EImageColorSpace::NO_CONVERSION;
            options.applyWhiteBalance = view.getApplyWhiteBalance();

            image::Image<image::RGBAfColor> image;
            image::readImage(viewPath, image, options);

            // Image color correction processing
            processColorCorrection(image, colorData);

            // Save image
            oiio::ParamValueList metadata = image::readImageMetadata(viewPath);
            image::writeImage(outputPath + "/" + std::to_string(viewId) + ".calibrated.jpg", image,
                              image::EImageColorSpace::NO_CONVERSION, metadata);

            // Update view for this modification
            view.setWidth(image.Width());
            view.setHeight(image.Height());
            view.setImagePath(outputPath + "/" + std::to_string(viewId) + ".calibrated.jpg");
        }

        // Save sfmData with modified path to images
        const std::string sfmfilePath = (fs::path(outputPath) / fs::path(inputExpression).filename()).generic_string();
        if(!sfmDataIO::Save(sfmData, sfmfilePath, sfmDataIO::ESfMData(sfmDataIO::ALL)))
        {
            ALICEVISION_LOG_ERROR("The output SfMData file '" << sfmfilePath << "' cannot be written.");

            return EXIT_FAILURE;
        }
    }
    else
    {
        // load input as image file or image folder
        const fs::path inputPath(inputExpression);
        std::vector<std::string> filesStrPaths;

        if(fs::is_regular_file(inputPath))
        {
            filesStrPaths.push_back(inputPath.string());
        }
        else
        {
            ALICEVISION_LOG_INFO("Working directory Path '" + inputPath.parent_path().generic_string() + "'.");

            const std::regex regex = utils::filterToRegex(inputExpression);
            // Get supported files in inputPath directory which matches our regex filter
            filesStrPaths = utils::getFilesPathsFromFolder(inputPath.parent_path().generic_string(),
                                                           [&regex](const boost::filesystem::path& path) {
                                                               return image::isSupported(path.extension().string()) &&
                                                                      std::regex_match(path.generic_string(), regex);
                                                           });
        }

        const int size = filesStrPaths.size();

        if(!size)
        {
            ALICEVISION_LOG_ERROR("Any images was found.");
            ALICEVISION_LOG_ERROR("Input folders or input expression '" << inputExpression << "' may be incorrect ?");
            return EXIT_FAILURE;
        }
        else
        {
            ALICEVISION_LOG_INFO(size << " images found.");
        }

        int i = 0;
        for(const std::string& inputFilePath : filesStrPaths)
        {
            ALICEVISION_LOG_INFO(++i << "/" << size << " - Process image at: '" << inputFilePath
                                     << "' for color correction.");

            // Create an image with 3 channel BGR color
            cv::Mat image = cv::imread(inputFilePath, cv::IMREAD_COLOR);

            // Check if the image is empty
            if(!image.data)
            {
                ALICEVISION_LOG_ERROR("Image at: '" << inputFilePath << "'" << "is empty.");

                return EXIT_FAILURE;
            }

            // Image color correction processing
            // cv::Mat calibratedImage = processColorCorrection(image, colorData);

            // Save the image
            // TODO
            // Example: saveImage(...)
            //const int outSize = 255;
            //calibratedImage.convertTo(calibratedImage,
            //                          CV_8UC3); // convert to 8 bits unsigned integer matrix / image with 3 channels
            //cv::Mat imgOut = min(max(calibratedImage, 0), outSize);
            //cv::Mat outImg;
            //cvtColor(imgOut, outImg, cv::COLOR_RGB2BGR);
            //cv::imwrite(outputPath + "/" + std::to_string(rand() % 1000 + 1) + ".calibrated.jpg", outImg);
        }
    }

    return EXIT_SUCCESS;
}
