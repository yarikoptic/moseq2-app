.PHONY: data

data:  data/test_session/proc/results_00.h5 data/test_session/proc/results_00.yaml data/test_session/proc/roi_00.tiff \
 data/test_session/metadata.json data/config.yaml data/test_session/depth_ts.txt data/test_session/test-out.avi \
 data/test_index.yaml data/azure_test/nfov_test.mkv data/test_model.p data/test_scores.h5


data/config.yaml:
	aws s3 cp s3://moseq2-app-test-data/moseq2-app/config.yaml data/ --request-payer=requester

data/test_index.yaml:
	aws s3 cp s3://moseq2-app-test-data/moseq2-app/test_index.yaml data/ --request-payer=requester

data/test_session/metadata.json:
	aws s3 cp s3://moseq2-app-test-data/moseq2-app/test_session/ data/test_session/ --request-payer=requester --recursive

data/test_session/proc/results_00.h5:
	aws s3 cp s3://moseq2-app-test-data/moseq2-app/test_session/proc/ data/test_session/proc/ --request-payer=requester --recursive

data/azure_test/nfov_test.mkv:
	aws s3 cp s3://moseq2-app-test-data/moseq2-extract/nfov_test.mkv data/azure_test/ --request-payer=requester

data/test_scores.h5:
	aws s3 cp s3://moseq2-app-test-data/moseq2-pca data/ --request-payer=requester --recursive

data/test_model.p:
	aws s3 cp s3://moseq2-app-test-data/moseq2-model data/ --request-payer=requester --recursive

