import os
import bokeh.io
import numpy as np
from copy import deepcopy
from os.path import exists
from unittest import TestCase
from moseq2_app.roi.controller import InteractiveFindRoi
from moseq2_extract.extract.proc import get_bground_im_file

class TestROIController(TestCase):

    @classmethod
    def tearDownClass(cls):
        if exists('data/session_config.yaml'):
            os.remove('data/session_config.yaml')

    def setUp(self):

        bokeh.io.output_notebook()
        self.gui = InteractiveFindRoi(data_path='data/',
                                      config_file='data/config.yaml',
                                      session_config='data/session_config.yaml',
                                      compute_bgs=True,
                                      autodetect_depths=True)
        self.gui.session_parameters['azure_test']['threads'] = 6
        self.gui.session_parameters['test_session']['threads'] = 6

    def tearDown(self):
        del self.gui

    def test_init(self):

        assert self.gui.sessions == {'test_session': 'data/test_session/test-out.avi',
                                     'azure_test': 'data/azure_test/nfov_test.mkv'}

        assert self.gui.keys == ['azure_test', 'test_session']

        session_parameters = {'test_session': deepcopy(self.gui.config_data),
                              'azure_test': deepcopy(self.gui.config_data)}

        assert list(self.gui.session_parameters.keys()) == ['azure_test', 'test_session']
        assert self.gui.all_results == {}

        assert self.gui.config_data['pixel_areas'] == []
        assert self.gui.config_data['autodetect'] == True
        assert self.gui.config_data['detect'] == True
        assert self.gui.in_test_all_sessions == False
        assert self.gui.session_parameters != session_parameters

    def test_generate_session_config(self):

        tmp_path = 'data/test_session.config'
        for k in self.gui.session_parameters:
            self.gui.session_parameters[k].pop('timestamps', None)
        self.gui.generate_session_config(tmp_path)

        assert exists(tmp_path)
        os.remove(tmp_path)

    def test_get_selected_session(self):

        selected_session = self.gui.checked_list.value

        # Creating a dummy event object to behave like a ipywidget callback object
        # with old and new object attributes
        class Event:
            old = selected_session
            new = selected_session
            def __init__(self, old=selected_session, new=selected_session):
                self.old = old
                self.new = new

        self.gui.config_data['detect'] = False
        self.gui.config_data['bg_roi_depth_range'] = [500, 700]

        event = Event()
        self.gui.get_selected_session(event)
        assert self.gui.config_data['detect'] == False

        # testing whether the detect attribute is being updated if old!=new
        event = Event(new=list(self.gui.checked_list.options)[1])
        self.gui.get_selected_session(event)

        assert self.gui.config_data['detect'] == True

    def test_compute_all_bgs(self):

        self.gui.compute_all_bgs()

        assert len(self.gui.session_parameters['azure_test']['timestamps']) == 66

    def test_extract_button_clicked(self):
        self.gui.session_parameters['azure_test']['bg_roi_depth_range'] = [300, 600]
        self.gui.session_parameters['azure_test']['bg_roi_erode'] = [1, 1]

        self.gui.main_out = None

        self.gui.interactive_find_roi_session_selector(self.gui.checked_list.value)
        self.gui.session_parameters['azure_test']['frame_range'] = [0, 60]
        self.gui.frame_range.value = [0, 60]

        self.gui.extract_button_clicked()

    def test_mark_passing_button_clicked(self):

        self.gui.interactive_find_roi_session_selector(self.gui.checked_list.value)

        num_areas = len(self.gui.config_data['pixel_areas'])
        self.gui.curr_results = {
                                 'roi': np.zeros((50,50)),
                                 'flagged': True,
                                 'ret_code': 'test',
                                 'counted_pixels': 54000
                                 }
        self.gui.mark_passing_button_clicked()

        assert self.gui.curr_results['ret_code'] == "0x1f7e2"
        assert self.gui.curr_results['flagged'] == False
        assert len(self.gui.config_data['pixel_areas']) == num_areas+1

    def test_check_all_sessions(self):

        self.gui.config_data['bg_roi_erode'] = [1, 1]

        self.gui.interactive_find_roi_session_selector(self.gui.checked_list.value)

        self.gui.check_all_sessions(None)

        assert all(list(self.gui.all_results.values())) == False

    def test_save_clicked(self):
        self.gui.config_data['bg_roi_depth_range'] = [500, 700]
        self.gui.config_data['bg_roi_erode'] = [1, 1]

        self.gui.interactive_find_roi_session_selector(self.gui.checked_list.value)

        self.gui.save_clicked()

        assert len(self.gui.config_data['pixel_areas']) > 0

    def test_update_minmax_config(self):
        self.gui.minmax_heights.value = [0, 101]
        self.gui.update_minmax_config(None)

        assert self.gui.config_data['min_height'] == 0
        assert self.gui.config_data['max_height'] == 101

    def test_update_config_fr(self):
        self.gui.frame_range.value = [0, 101]
        self.gui.update_config_fr(None)

        assert self.gui.config_data['frame_range'] == (0, 101)

    def test_all_sessions(self):

        self.gui.config_data['bg_roi_depth_range'] = [500, 700]
        self.gui.config_data['bg_roi_erode'] = [1, 1]

        # Add true depth to both session such that new range won't be computed
        # Refelecting on the changes setting config_data['autodetect'] to True
        # when there is no depth to compute the true depth and range
        self.gui.session_parameters['azure_test']['true_depth'] = 514
        self.gui.session_parameters['test_session']['true_depth'] = 49255

        self.gui.interactive_find_roi_session_selector(self.gui.checked_list.value)

        self.gui.test_all_sessions(self.gui.sessions)

        assert list(self.gui.all_results.keys()) == ['azure_test', 'test_session']
        assert list(self.gui.all_results.values()) == [False, True]
        assert self.gui.in_test_all_sessions == False

    def test_interactive_find_roi_session_selector(self):
        self.gui.config_data['bg_roi_depth_range'] = [500, 700]
        self.gui.config_data['bg_roi_erode'] = [1, 1]

        self.gui.interactive_find_roi_session_selector(self.gui.checked_list.value)

        assert self.gui.curr_bground_im.shape == (576, 640)
        assert self.gui.curr_session == 'data/azure_test/nfov_test.mkv'

    def test_update_checked_list(self):

        curr_options = deepcopy(list(self.gui.checked_list.options))

        # initialize an example results dict for a passing session
        sample_passing_ex = {
            'flagged': False, # passing
            'ret_code': '0x1f7e2', # ret_code -> green dot
            'counted_pixels': 0
        }

        # get first instance of self.curr_results indicating that the given session is failing
        self.gui.interactive_find_roi_session_selector(self.gui.checked_list.value)

        # session returned flagged
        assert self.gui.curr_results['flagged'] == True # session is not passing
        assert self.gui.curr_results['ret_code'] == '0x1f534' # curr results is a red dot
        # checked_list options are unchanged; all still failing
        assert curr_options == list(self.gui.checked_list.options)

        # update the value of self.gui.checked_list.options, not self.curr_results
        self.gui.update_checked_list(sample_passing_ex)

        # since self.gui.checked_list.options was updated, the indicator color must be updated
        assert curr_options != list(self.gui.checked_list.options)

    def test_interactive_depth_finder(self):

        self.gui.config_data['bg_roi_depth_range'] = [500, 700]
        self.gui.config_data['bg_roi_erode'] = [1, 1]

        minmax_heights = [0, 100]
        fn = 0
        dr = [500, 700]
        di = 1

        curr_session_key = self.gui.keys[self.gui.checked_list.index]
        config_before = deepcopy(self.gui.session_parameters[curr_session_key])

        self.gui.formatted_key = self.gui.checked_list.value.split(' ')[1]
        self.gui.curr_session = self.gui.sessions[self.gui.formatted_key]
        self.gui.curr_bground_im = get_bground_im_file(self.gui.curr_session, **self.gui.session_parameters[curr_session_key])

        self.gui.interactive_depth_finder(minmax_heights, fn, dr, di)

        # autodetect is true, so the depth range will not be the same as originally set
        assert self.gui.session_parameters[curr_session_key]['bg_roi_depth_range'] == (414, 614)
        assert self.gui.session_parameters[curr_session_key] != config_before
        assert self.gui.curr_results['ret_code'] == '0x1f7e2'

    def test_prepare_data_to_plot(self):

        self.gui.config_data['bg_roi_depth_range'] = [100, 700]
        self.gui.config_data['bg_roi_erode'] = [1, 1]

        minmax_heights = [1, 101]
        fn = 0
        self.gui.interactive_find_roi_session_selector(self.gui.checked_list.value)
        self.gui.prepare_data_to_plot(self.gui.curr_results['roi'], minmax_heights, fn)

        assert self.gui.session_parameters['azure_test']['min_height'] == int(minmax_heights[0])
        assert self.gui.session_parameters['azure_test']['max_height'] == int(minmax_heights[1])
        assert self.gui.session_parameters['azure_test']['true_depth'] == int(self.gui.true_depth)
