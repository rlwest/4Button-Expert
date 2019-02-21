## uses only RP and AK planning units and unit tasks, so far
## perception of the game is hacked, so far



import sys

sys.path.append('/Users/robertwest/CCMSuite')
#sys.path.append('C:/Users/Robert/Documents/Development/SGOMS/CCMSuite')
import ccm
from random import randrange, uniform
log = ccm.log()
# log=ccm.log(html=True)
from ccm.lib.actr import *






class MyEnvironment(ccm.Model):
    
    warning_light = ccm.Model(isa='warning_light', state='off')
    response = ccm.Model(isa='response', state='none')
    code = ccm.Model(isa='code', state='SU') # model assumes it starts at AK and doen't look until it has to


    motor_finst = ccm.Model(isa='motor_finst', state='re_set')


class MotorModule(ccm.Model):
    
##    def maybe_change_light(self):
##        irand = randrange(0, 30) # adjust warning light probability here
##        if irand < 1: 
##           print ' light on ++++++++++++++++++++++++++++++++++++++++++++++++++++'
##           print irand
##           self.parent.parent.warning_light.state='on'         
##
##    def turn_off_light(self):
##        self.parent.parent.warning_light.state='off'
##        print 'light off ------------------------------------------------------'
##
# change_state is a generic action that changes the state slot of any object
# disadvantages (1) yield #time is always the same (2) cannot use for parallel actions


    def change_state_fast(self, env_object, slot_value):
        yield 3
        x = eval('self.parent.parent.' + env_object)
        x.state = slot_value
        print env_object
        print slot_value
        self.parent.parent.motor_finst.state = 'change_state_fast'

    def vision_slow(self):
        yield 5
        print 'target identified'
        self.parent.parent.motor_finst.state = 'vision_slow'
        self.parent.b_vision.set('YP')

    def motor_finst_reset(self):
        self.parent.parent.motor_finst.state = 're_set'



class EmotionalModule(ccm.ProductionSystem):
    production_time = 0.043
##    def warning_light(b_emotion='threat:ok',warning_light='state:on'):
##        print "warning light is on!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!"
##        b_emotion.set('threat:high')


       


class Environment_Manager(ACTR): # this agent triggers the warning light
    b_focus = Buffer()
    motor = MotorModule()
##    def init():
##        b_focus.set('set_warning')
##    def environment(b_focus='set_warning'):
##        motor.maybe_change_light()


class MyAgent(ACTR): # this is the agent that does the task

    # module buffers
    b_DM = Buffer()
    b_motor = Buffer()
    b_focus = Buffer()
    b_vision = Buffer()

    # goal buffers
    b_context = Buffer()
    b_plan_unit = Buffer() 
    b_unit_task = Buffer()
    b_method = Buffer()
    b_operator = Buffer()
    b_emotion = Buffer()

    DM = Memory(b_DM)  
    motor = MotorModule(b_motor)
    Emotion = EmotionalModule(b_emotion)  


    def init():
##        DM.add('planning_unit:XY         cuelag:none          cue:start          unit_task:X')
##        DM.add('planning_unit:XY         cuelag:start         cue:X              unit_task:Y')
##        DM.add('planning_unit:XY         cuelag:X             cue:Y              unit_task:finished')

        DM.add('planning_unit:AK         cuelag:none          cue:start          unit_task:AK')
        DM.add('planning_unit:AK         cuelag:start         cue:AK              unit_task:RP')
        DM.add('planning_unit:AK         cuelag:AK             cue:RP              unit_task:finished')

        DM.add('planning_unit:RP         cuelag:none          cue:start          unit_task:RP')
        DM.add('planning_unit:RP         cuelag:start         cue:RP              unit_task:AK')
        DM.add('planning_unit:RP         cuelag:RP             cue:AK              unit_task:finished')
        
        b_context.set('finshed:nothing status:unoccupied warning_light:off')
        b_emotion.set('threat:ok')
        b_focus.set('none')
        b_vision.set('AK') # assume this has happened



    
########################### begin the planning unit

# these productions are the highest level of SGOMS and fire off the context buffer
# the decision process can be as complex as needed
# the simplest way is to have a production for each planning unit (as in this case)
# the first unit task in the planning unit is directly triggered from here

    def run_PU_AK(b_context='finshed:nothing status:unoccupied',
                  b_vision='AK'):        
        b_unit_task.set('unit_task:AK state:running typee:ordered')
        b_plan_unit.set('planning_unit:AK cuelag:none cue:start unit_task:AK state:running')
        b_context.set('finished:nothing status:occupied')
        print 'PU_AK ordered planning unit is chosen OOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOO'

    def run_PU_RP(b_context='finshed:AK status:unoccupied'):
        b_unit_task.set('unit_task:RP state:running typee:ordered')
        b_plan_unit.set('planning_unit:RP cuelag:none cue:start unit_task:RP state:running')
        b_context.set('finished:nothing status:occupied')
        print 'PU_RP ordered planning unit is chosen OOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOO'

    def end(b_context='finshed:RP status:unoccupied'):
        b_context.set('end')
        print 'end program'

    def false_alarm(b_context='finshed:?finished status:interupted'):
        motor.turn_off_light()
        b_emotion.set('threat:ok')
        b_unit_task.set('unit_task:X state:running typee:ordered')
        b_plan_unit.set('planning_unit:XY cuelag:none cue:start unit_task:X state:running')
        b_context.set('finished:nothing status:occupied')
        print 'ordered planning unit is chosen OOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOO'



######################### planning unit management loop
# these are generic productions for managing the execution of planning units

######## get next unit task and save a memory of the completed unit task

# the first unit task in a planning unit is triggered when the planning unit is chosen
# these porductions fire within planning units to get the next unit task
# to trigger the next unit task the unit_task state slot value is switched from 'end' to 'begin'
# this is also where the successful completion of the last unit task is saved to memory
## the memory save is often not needed in simple models and is not implemented here
### although, in theory, the memory save always happens so this step should always be included


# ordered planning units

## retrieve next unit task
    def request_next_unit_task(b_plan_unit='planning_unit:?planning_unit cuelag:?cuelag cue:?cue unit_task:?unit_task state:running',
                               b_unit_task='unit_task:?unit_task state:end typee:ordered',
                               b_emotion='threat:ok'):
        DM.request('planning_unit:?planning_unit cue:?unit_task unit_task:? cuelag:?cue')
        b_plan_unit.set('planning_unit:?planning_unit cuelag:?cuelag cue:?cue unit_task:?unit_task state:retrieve')  # next unit task
        print 'finished unit task = ', unit_task
        # save completed unit task here
    def retrieved_next_unit_task(b_plan_unit='state:retrieve',
                                 b_DM='planning_unit:?planning_unit cuelag:?cuelag cue:?cue unit_task:?unit_task!finished'):
        b_plan_unit.set('planning_unit:?planning_unit cuelag:?cuelag cue:?cue unit_task:?unit_task state:running')
        b_unit_task.set('unit_task:?unit_task state:running typee:ordered')
        print 'next unit_task = ', unit_task
        print 'ordered'


# situated planning units

## allow the next unit task to fire
    def next_situated_unit_task(b_unit_task='unit_task:?unit_task state:end typee:situated',
                                b_emotion='threat:ok'):
        b_unit_task.modify(state='find_match') 
        print 'next situated unit task'
        print 'situated'
        # save unit task here



########### end the planning unit and save a memory of it
        
# a planning unit can be thought of as a loop
# these are the exit conditions
# in these the planning unit should be saved
# although, to keep the code simple, this is not done here

## finished ordered planning unit
    def retrieved_last_unit_task(b_plan_unit='planning_unit:?planning_unit state:retrieve',
                                 b_unit_task='unit_task:?unit_task state:end typee:ordered',
                                 b_DM='planning_unit:?planning_unit cuelag:?cuelag cue:?cue unit_task:finished'):
                                    # not, the memory retrieval indicates the plan is finished
        print 'stopped planning unit=',planning_unit
        print 'finished'
        b_unit_task.modify(state='stopped') 
        b_context.set('finshed:?planning_unit status:unoccupied')
        # save completed planning unit here



    def interupted_planning_unit(b_plan_unit='planning_unit:?planning_unit',
                                 b_unit_task='unit_task:?unit_task state:end typee:?typee',
                                 b_emotion='threat:high'):
        print 'stopped planning unit='
        print 'interupted IIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIII'
        b_unit_task.modify(state='stopped') 
        b_context.set('finshed:?planning_unit status:interupted')
        # save completed planning unit here





####################################### unit tasks


# AK unit task AK-WM-SU-ZB-FJ

## situated matching productions

    def AK_start_unit_task_situated(b_unit_task='state:find_match typee:situated'):
        b_unit_task.set('unit_task:AK state:running typee:situated')
        print 'start unit task AK'

## body of the unit task
        
    def AK_known_response_AK(b_unit_task='unit_task:AK state:running',
                             b_focus='none'):
        b_focus.set('AK')
        b_method.set('method:known_response target:response content:1234 state:start')
        print 'AK unit task    AAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAA'
        print 'doing AK'

    def AK_known_response_WM(b_unit_task='unit_task:AK state:running',
                          b_focus='AK',
                          b_method='state:finished'):
        b_focus.set('WM')
        b_method.set('method:known_response target:response content:1432 state:start')
        print 'doing WM'

    def AK_known_response_SU(b_unit_task='unit_task:AK state:running',
                          b_focus='WM',
                          b_method='state:finished'):
        b_focus.set('SU')
        b_method.set('method:known_response target:response content:4123 state:start')
        print 'doing SU'

    def AK_known_response_ZB(b_unit_task='unit_task:AK state:running',
                          b_focus='SU',
                          b_method='state:finished'):
        b_focus.set('ZB')
        b_method.set('method:known_response target:response content:2143 state:start')
        print 'doing ZB'

    def AK_known_response_FJ(b_unit_task='unit_task:AK state:running',
                          b_focus='ZB',
                          b_method='state:finished'):
        b_focus.set('FJ')
        b_method.set('method:known_response target:response content:3214 state:start')
        print 'doing FJ'

    def AK_finished(b_unit_task='unit_task:AK state:running',
                 b_focus='FJ',
                 b_method='state:finished'):
        b_focus.set('none')
        b_unit_task.modify(state='end')  ## this line ends the unit task
        print ' - finished unit task'

#                    YP-FJ
# RP unit task RP-SU<
#                    ZB-WM

## situated matching productions

    def RP_start_unit_task_situated(b_unit_task='state:find_match typee:situated'):
        b_unit_task.set('unit_task:Y state:running typee:situated')
        print 'start unit task Y'

## body of the unit task
        
    def RP_known_response_RP(b_unit_task='unit_task:RP state:running',
                             b_focus='none'):
        b_focus.set('RP')
        b_method.set('method:known_response target:response content:4321 state:start')
        print 'doing RP_UT    RRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRR'
        print 'doing RP'

    def RP_known_response_SU(b_unit_task='unit_task:RP state:running',
                             b_focus='RP',
                             b_method='state:finished'):
        b_focus.set('SU')
        b_method.set('method:known_response target:response content:4123 state:start')
        print 'doing SU'

    def RP_unknown_code(b_unit_task='unit_task:RP state:running',
                        b_focus='SU',
                        b_method='state:finished'):
        b_focus.set('unkown_code')
        b_method.set('method:get_code target:response content:1432 state:start')
        print 'getting code'


    def RP_got_code1(b_unit_task='unit_task:RP state:running',
                     b_focus='unkown_code',
                     b_method='state:finished',
                     b_vision='YP'):
        b_focus.set('YP')
        b_method.set('method:known_response target:response content:1432 state:start')
        print 'doing YP'

    def RP_known_response_FJ(b_unit_task='unit_task:RP state:running',
                             b_focus='YP',
                             b_method='state:finished'):
        b_focus.set('FJ')
        b_method.set('method:known_response target:response content:3214 state:start')
        print 'doing FJ'

    def RP_finished1(b_unit_task='unit_task:RP state:running',
                     b_focus='FJ',
                     b_method='state:finished'):
        b_focus.set('none')
        b_unit_task.modify(state='end')  ## this line ends the unit task
        print ' - finished unit task'

    def RP_got_code2(b_unit_task='unit_task:RP state:running',
                     b_focus='unkown_code',
                     b_method='state:finished',
                     b_vision='ZB'):
        b_focus.set('ZB')
        b_method.set('method:known_response target:response content:1432 state:start')
        print 'doing ZB'

    def RP_known_response_WM(b_unit_task='unit_task:RP state:running',
                             b_focus='ZB',
                             b_method='state:finished'):
        b_focus.set('WM')
        b_method.set('method:known_response target:response content:2143 state:start')
        print 'doing WM'

    def RP_finished2(b_unit_task='unit_task:Y state:running',
                     b_focus='WM',
                     b_method='state:finished'):
        b_focus.set('none')
        b_unit_task.modify(state='end')  ## this line ends the unit task
        b_unit_task.modify(state='stop')  ## this line ends the unit task
        print ' - finished unit task'


###################################################### methods ###################################################################
##################################################################################################################################

# known response method #########################
# the response is passed down by the production that called this method

    def known_response_vision(b_method='method:known_response target:?target content:?content state:start'):  # target is the chunk to be altered
        motor.change_state_fast(target, content)
        b_method.modify(state='running')
        print 'entering response'
        print 'target object = ', target

    def response_entered(b_method='method:?method target:?target state:running',
                         motor_finst='state:change_state_fast'):
        b_method.modify(state='finished')
        motor.motor_finst_reset()
        print 'I have altered - ', target


# get_code method ################################
# in the case where the next response depends on the code the agent must first read the code

    def get_code(b_method='method:get_code target:?target content:?content state:start'):  # target is the chunk to be altered
        motor.vision_slow()
        b_method.modify(state='running')
        print 'getting code'

    def get_code_finished(motor_finst='state:vision_slow',
                          b_vision='?code'):
        motor.motor_finst_reset()
        b_method.modify(state='finished')
        print 'I have spotted the target, I have the new code'
        print code


############## run model #############
        
jim = Environment_Manager()
tim = MyAgent()  # name the agent
subway = MyEnvironment()  # name the environment
subway.agent = tim  # put the agent in the environment
subway.agent = jim  # put the agent in the environment

ccm.log_everything(subway)  # print out what happens in the environment
subway.run()  # run the environment
ccm.finished()  # stop the environment
