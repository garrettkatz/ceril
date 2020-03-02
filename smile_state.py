import assembly as asm

class SmileState(object):

    def __init__(self):

        tabletop = asm.block("tabletop")

        self.things = {"tabletop": tabletop}
        self.support = {"tabletop": "nothing"}
        self.gripping = {"LeftHand": "nothing", "RightHand": "nothing"}
    
    def tree_string(self):
        s = "%s in left, %s in right" % (self.gripping["LeftHand"], self.gripping["RightHand"])
        for name, thing in self.things.items():
            s += "\n%s on %s" % (thing, self.support[name])
        return s
    
    def copy(self):
        state = SmileState()
        state.things = dict(self.things)
        state.support = dict(self.support)
        state.gripping = dict(self.gripping)
        return state

def load_from_smile_txt(fname):

    state = SmileState()

    with open(fname,"r") as txt:
        for line in txt:
            tokens = line.strip().split(",")
            idx, event = tokens[:2]
            if event == "create":
                name, object_type = tokens[2], tokens[4]
                state.things[name] = asm.Assembly(object_type, [], name)
                state.support[name] = "tabletop"

    return state

#         %%% Loads state from first output text file of tabletop demos
#             stt = State.makeSimulator();
#             table = State.getThing(stt, 'table');
#             table_offset = table.t;
#             [V,~,~,~] = Assembly.placed(table);
#             %table_offset(3) = table_offset(3)+max(V(3,:));
#             table_offset(3) = max(V(3,:));
#             fid = fopen(fname);
#             line = fgetl(fid);
#             % valve settings
#             is_valves = false;
#             ball_swivel_id = '';
#             screw_rotations = nan;
#             ball_open = true;
#             leds_on = false(1,3);
#             % Smile shapes have different centers
#             % offset = matlab center - smile center
#             [plumbing_offset, screw_offset] = BaxterConfig.smileValveOffsets();
#             screw_holder_t = nan(3,1); % account for sub-assembly in matlab but not smile
#             screw_holder_id = nan;
#             % Parse lines
#             while ischar(line)
#                 strs = strsplit(line,',');
#                 % Switch on action name
#                 if strcmp(strs{2},'create')
#                     % Get object id and shape
#                     label = strs{3};
#                     shape = strs{5};
#                     % Gather property:value pairs in struct and extract
#                     attr = struct(strs{6:end});
#                     if strcmp(shape,'block')
#                         dims = [str2double(attr.width); str2double(attr.depth); str2double(attr.height)];
#                         if any(strcmp('color',fieldnames(attr)))
#                             color = [hex2dec(attr.color(end-5:end-4)); hex2dec(attr.color(end-3:end-2)); hex2dec(attr.color(end-1:end))]/255.0;
#                             color = color/norm(color);
#                         else
#                             color = [0 0 1]';
#                         end
#                         asm = Assembly.makeFreeBlock(dims, color);
#                         asm = Assembly.setLabel(asm, label);
#                         stt.things(label) = Assembly.place(asm, eye(3), table_offset);
#                     elseif strcmp(shape,'cartridge')
#                         color = [hex2dec(attr.color(end-5:end-4)); hex2dec(attr.color(end-3:end-2)); hex2dec(attr.color(end-1:end))]/255.0;
#                         color = color/norm(color);
#                         handle_color = [hex2dec(attr.handleColor(end-5:end-4)); hex2dec(attr.handleColor(end-3:end-2)); hex2dec(attr.handleColor(end-1:end))]/255.0;
#                         handle_color = handle_color/norm(handle_color);
#                         asm = Assembly.makeCartridge(color, handle_color, handle_color);
#                         asm = Assembly.setLabel(asm, label);
#                         % Add object to state
#                         stt.things(label) = Assembly.place(asm, eye(3), table_offset);
#                     elseif strcmp(shape,'dock-body')
#                         asm = Assembly.makeDockDrawer();
#                         asm = Assembly.setLabel(asm, 'dock-body');
#                         stt.things('dock-body') = Assembly.place(asm, eye(3), table_offset);
#                     elseif strcmp(shape,'dock-case')
#                         asm = Assembly.makeDockCase(true);
#                         asm = Assembly.setLabel(asm, 'dock-case');
#                         stt.things('dock-case') = Assembly.place(asm, eye(3), table_offset);
#                     elseif strcmp(label,'valve_screw')
#                         asm = Assembly.makeValveScrew();
#                         asm = Assembly.setLabel(asm, 'valve_screw');
#                         stt.things('valve_screw') = Assembly.place(asm, eye(3), table_offset);
#                     elseif any(strcmp(label,{'spare1','spare2','spare3'})) % spare valves, pending smile composite type labels
#                         asm = Assembly.makeValveScrew();
#                         asm = Assembly.setLabel(asm, label);
#                         stt.things(label) = Assembly.place(asm, eye(3), table_offset);
#                     elseif strcmp(label,'ball_swivel')
#                         ball_swivel_id = 'ball_swivel';
#                     elseif strcmp(label,'screw_holder')
#                         % actual assembly added via plumbing
#                     elseif strcmp(label,'plumbing')
#                         % ball swivel, stepper added automatically
#                         is_valves = true;
#                         module_mult = [-1,1,0]; % stopgap for default smile plumbing
#                         asm = Assembly.makeValves(module_mult);
#                         asm = Assembly.setLabel(asm, 'valves');
#                         stt.things('valves') = Assembly.place(asm, eye(3), table_offset);
#                         % update screw holder id
#                         screw_holder_id = 'screw_holder';
#                         [holder, holder_root_id, holder_path] = State.getAssemblyByType(stt,'screw_holder');
#                         holder = Assembly.setLabel(holder,screw_holder_id);
#                         stt = State.setThing(stt, holder, holder_root_id, holder_path);
#                     elseif strcmp(label(1:4), 'ring')
#                         outradius = str2double(strrep(label(5:end),'_','.'));
#                         asm = Assembly.makeHanoiRing(outradius,[1;0;0]);
#                         asm = Assembly.setLabel(asm, label);
#                         stt.things(label) = Assembly.place(asm, eye(3), table_offset);
#                     elseif strcmp(label, 'poles')
#                         asm = Assembly.makeHanoiPoles();
#                         asm = Assembly.setLabel(asm, label);
#                         stt.things(label) = Assembly.place(asm, eye(3), table_offset);
#                     end
#                 elseif strcmp(strs{2},'move')
#                     % Get object by id
#                     label = strs{3};
#                     % Reposition object
#                     t = [str2double(strs{4}); str2double(strs{5}); str2double(strs{6})];
#                     Rx = Geom.planeRotation(str2double(strs{7})*pi/180,2,3,3);
#                     Ry = Geom.planeRotation(str2double(strs{8})*pi/180,3,1,3);
#                     Rz = Geom.planeRotation(str2double(strs{9})*pi/180,1,2,3);
#                     %if any(strcmp(label,{'stepper_screw','screw_holder'}))
#                     if any(strcmp(label,{'stepper_screw'}))
#                         % do nothing
#                     elseif strcmp(label,ball_swivel_id)
#                         za = str2double(strs{9});
#                         [~,idx] = min(abs([za; za+90]));
#                         ball_open = (idx == 1);
#                     else
#                         if strcmp(label,'plumbing')
#                             label = 'valves';
#                             t = t + plumbing_offset;
#                         elseif any(strcmp(label,{'valve_screw','spare1','spare2','spare3'}))
#                             t = t + screw_offset;
#                         elseif strcmp(label,screw_holder_id)
#                             screw_holder_M = Rz*Ry*Rx;
#                             screw_holder_t = table_offset + t;
#                         end
#                         stt = State.placeThing(stt, label, Rz*Ry*Rx, table_offset + t);
# %                         if strcmp(label,screw_holder_id)
# %                             cla; hold on; State.show3d(stt);
# %                             input('./?2');
# %                         end
#                     end
#                 elseif strcmp(strs{2},'initializeControl')
                    
#                     led_str = strs{6};
#                     if any(strcmp(led_str,{'0','1','2','3'})), leds_on = [true,true,true]; end;
#                     if strcmp(led_str,'4'), leds_on = [true,true,false]; end;
#                     if strcmp(led_str,'5'), leds_on = [true,false,false]; end;
#                     if strcmp(led_str,'6'), leds_on = [false,false,false]; end;
                    
#                 end
#                 line = fgetl(fid);
#             end
#             fclose(fid);
#             % Special valves handling:
#             if is_valves
#                 % get screw rotations before dropping, use relative z to get rotations
#                 [screw,~,~] = State.getThing(stt,'valve_screw');
#                 [valves,~,~] = State.getThing(stt,'valves');
#                 chassis_path = [1, 4];
#                 chassis = Assembly.getSubAssembly(valves, chassis_path);
#                 screw_dt = screw.t - (chassis.t+[0;0;STLShape.i2d(1.85)]);
#                 % check if screw in chassis
#                 if -.1 <= screw_dt(3) && screw_dt(3) <= 4*STLShape.i2d(.3875) + .1 && norm(screw_dt(1:2)) < .2
#                     screw_rotations = screw_dt(3)/STLShape.i2d(.3875);
#                 end
#                 % rename ball swivel
#                 [ball_swivel, root_id, path] = State.getAssemblyByType(stt,'ball_swivel');
#                 ball_swivel.label = ball_swivel_id;
#                 ball_swivel = Assembly.assignIDs(ball_swivel, ball_swivel_id);
#                 stt = State.setThing(stt, ball_swivel, root_id, path);
#                 % update screw holder position
#                 if ~any(isnan(screw_holder_t)) % check if screw holder in this example
#                     stt = State.placeThing(stt, screw_holder_id, screw_holder_M, screw_holder_t);
#                 end
#             end
#             % Set supports
#             labels = keys(stt.things);
#             % Assign ids to everything
#             for i = 1:numel(labels)
#                 asm = stt.things(labels{i});
#                 asm = Assembly.assignIDs(asm, labels{i});
#                 stt.things(labels{i}) = asm;
#             end
#             for i = 1:numel(labels)
#                 if strcmp(labels{i},'dock-body')
#                     [stt, dock_body] = State.removeThing(stt, 'dock-body');
#                     [dock_case, root_id, path] = State.getThing(stt, 'dock-case');
#                     dock_case = Assembly.addSubAssembly(dock_case, dock_body, [1]);
#                     stt = State.setThing(stt, dock_case, root_id, path);
#                     remove(stt.things, 'dock-body');
#                 elseif strcmp(labels{i},'dock-case')
#                     [stt, dock_case] = State.removeThing(stt, 'dock-case');
#                     [table, root_id, path] = State.getThing(stt, 'table');
#                     table = Assembly.addSubAssembly(table, dock_case, []);
#                     stt = State.setThing(stt, table, root_id, path);
#                     remove(stt.things, 'dock-case');
#                 elseif strcmp(labels{i},'valves')
#                     [stt, valves] = State.removeThing(stt, 'valves');
#                     [table, root_id, path] = State.getThing(stt, 'table');
#                     table = Assembly.addSubAssembly(table, valves, []);
#                     stt = State.setThing(stt, table, root_id, path);
#                     remove(stt.things, 'valves');
#                 elseif any(strcmp(labels{i},{'valve_screw','spare1','spare2','spare3'}))
#                 elseif any(strcmp(labels{i},{'ball_swivel','stepper_screw'}))
#                 else
#                     %disp(labels{i})
#                     stt = State.dropOnAssembly(stt, labels{i});
#                 end
#             end

#             % Update valves state
#             if is_valves
#                 disp(ball_open)
#                 stt = State.setValvesState(stt, leds_on, ball_open);
#                 if ~isnan(screw_rotations)
#                     stt = State.setValveScrew(stt, 'valve_screw', screw_rotations);
#                 end
#                 % update screws in holder
#                 for spare = 1:3
#                     screw_id = sprintf('spare%d',spare);
#                     [tf, holder_idx] = State.screwInHolder(stt, screw_id);
#                     if tf
#                         stt = State.setHolderScrew(stt, screw_id, holder_idx);
#                     end
#                 end
#             end
#         end


if __name__ == "__main__":

    # print(SmileState())
    state = load_from_smile_txt("demos/test/0.txt")
    print(state.tree_string())
