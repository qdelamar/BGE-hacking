#!/usr/bin/python3

#2020-05


### read source binary:
nf=open("bge.exe","rb")
patched=[int(c) for c in nf.read()]
nf.close()


### patch helpers:
def patch(addr,value,size=1):
	value%=1<<(8*size) # mainly for negative addresses
	for k in range(size):
		patched[addr-0x400000+k]=(value>>(8*k))%256

seek=0
def wp(value,size=1):
	global seek
	patch(seek,value,size)
	seek+=size

def jmp(to):
	global seek
	patch(seek,0xe9)
	patch(seek+1,to-seek-5,4)
	seek+=5

def call(func):
	global seek
	patch(seek,0xe8)
	patch(seek+1,func-seek-5,4)
	seek+=5


### keyboard mapping in game:
keys={'o':0x18,'k':0x25,'l':0x26,'m':0x32,'u':0x16} # i have only searched these ones but others are available if needed


### let's patch it baby:
base=0xb36cb0 # there is some room here to write our patches


##force peyj walking code to execute all the time:
patch(0xa08b2c,0xeb)


##remove jade's-position-based zone restriction:
# side-effect: peyj wont talk anymore and may not follow jade into beluga (to be checked) (todo: find a way to improve that)
patch(0x53a8e4,0xeb) # you can comment this if you prefer


##set peyj speed depending on keyboard:
frm=0xa08bea
seek=frm
jmp(base) # deviation to patch at base
wp(0x90) # fill the hole

seek=base
wp(0xba)
wp(0xba1720,4) # keys array start

wp(0xb9)
#wp(base-12,4) # no, this is not writable!
wp(0xb66ff0,4) # ecx = 3d vector pointer (this zone seems free...)

#init:
wp(0xfc41c6,3) # [ecx-4]
wp(0) # =(char)0 <= just a state to know if we want to move or not
wp(0x0041c7,3) # x at [ecx] => lateral moves in camera frame
wp(0,4) # =(float)0
wp(0x0441c7,3) # y at [ecx+4] (not used but necessary here)
wp(0,4) # =(float)0
wp(0x0841c7,3) # z at [ecx+8] => forward/backward axis in camera frame
wp(0,4) # =(float)0

wp(0x7a80,2) # if
wp(keys['l']) # down key
wp(0x80)
wp(0x0b75,2) # (else:jmp to next test)
wp(0x0841c7,3) # set z
wp(0xbf800000,4) # =(float)-1
wp(0xfc41c6,3) # set [ecx-4]
wp(1) # =1

wp(0x7a80,2) # if
wp(keys['o']) # up key
wp(0x80)
wp(0x0b75,2) # (else:jmp to next test)
wp(0x0841c7,3) # set z
wp(0x3f800000,4) # =(float)1
wp(0xfc41c6,3) # set [ecx-4]
wp(1) # =1

wp(0x7a80,2) # if
wp(keys['k']) # left key
wp(0x80)
wp(0x0b75,2) # (else:jmp to next test)
wp(0x0041c7,3) # set x
wp(0xbf800000,4) # =(float)-1
wp(0xfc41c6,3) # set [ecx-4]
wp(1) # =1

wp(0x7a80,2) # if
wp(keys['m']) # right key
wp(0x80)
wp(0x0b75,2) # (else:jmp to next test)
wp(0x0041c7,3) # set x
wp(0x3f800000,4) # =(float)1
wp(0xfc41c6,3) # set [ecx-4]
wp(1) # =1

wp(0x24048b,3) # animation pointer is on the stack
wp(0x00fc7980,4) # if move
wp(0x0875,2) # jne

wp(0x1e00c6,3) # stand animation 0x1e (others are possible)
jmp(frm+11) # jmp back after the next call to ignore it

wp(0x7a80,2) # if
wp(keys['u']) # run key
wp(0x80)
wp(0x0574,2) # then goto run
wp(0x0300c6,3) # else walk with animation 0x03
wp(0x03eb,2) # jmp to next

wp(0x0200c6,3) # run with animation 0x02


#rotate command vector into camera frame (instead of world frame):
wp(0xbe) # esi=
wp(0xd0a420,4) # cam pose

#need to get inv matrix:
wp(0xb8) # eax=
wp(0xb66f80,4) # free space (?)
call(0x425870) # inverse 4x4 transform of the camera @esi into @eax (this affects ecx & edx)

wp(0xc189,2) # ecx=inversed ori

wp(0xb8) # eax=
wp(0xb66ff0,4) # command vector in camera frame

#wp(0xb0558d,3) # at the end ecx will be this pointer, for now it's edx
wp(0xba) # edx=
wp(0xb66fe0,4) # use a free place not used otherwise for live debug
call(0x425290) # rotate vec @eax with matrix @ecx into @edx
wp(0xd189,2) # ecx=result

wp(0xcc558d,3) # prepare edx for the coming call
jmp(frm+5) # jmp back to normal code


#todo: implement other animations that would be cool: 1=walk slowly, 0x0d=hiii, and maybe some jumping/climbing stuff (0x08,0x0a,0x0c,0x1c,..?)






## set some state values to force loading peyj and enable him moving (in the beginning of the loading):
#set a state to not 4 at loading (there might be an easier way but it's the only way i found for now):
patch2=base+200
patch(patch2-4,0x90909090,4) # just for readability for debug
frm2=0x496bfa # the value we're interested in was written by the code just before this, let's spoil that
seek=frm2
jmp(patch2) # deviation from original code
seek=patch2
call(0x495b00) # do the original call that we just smashed

#set *(*0xb80664+4)=0x4f
wp(0x3d8b,2) # edi will not interfer bcz it's pop'd just after this patch
wp(0xb80664,4)
wp(0x00ff83,3) # check if null pointer, bcz this patch may be called at the very beginning before this pointer is set
wp(0x0474,2) # if null do nothing
wp(0x4f0447c6,4) # else put 0x4f in there
jmp(frm2+5) # return to main code




#ensure that peyj is loaded by forcing a loading code to execute (end of loading):
patch4=base+250
patch(patch4-4,0x90909090,4)
frm4=0x6a242b
seek=frm4
jmp(patch4)
seek=patch4
call(0xabf8e0)
wp(0xa1)
wp(0xb80664,4)
wp(0x020468c0,4) # *(eax+4)>>=2, so that it goes from 0x4f to 0x13 to 0x04
#wp(0x010468c0,4) # *(eax+4)>>=1
#wp(0x0448fe,3) # *(eax+4)-- until it reaches 4... that's ugly but i dont have any better solution for now
jmp(frm4+5)

#seems that peyj wont appear if this is done once (nor twice) without a debug breakpoint!!
#which means that something else actually makes him appear, idk where (probably in another thread considering this strange debug-related behavior)
#so a ugly fix is to do this a lot of times to make sure the unknown code gets executed...





#correction of a WRONG testing code in the original binary, which is BY LUCK NEVER REACHED in normal game but that may be reached and NOT PROPERLY HANDLED when debugging. yes really.
seek=0x49db97
wp(0x21) # if the pointer is 0 we need to exit the function directly, which was not the case in the initial binary leading to sigsegv right after when calling the recursive sub-object exploring stuff at 0x468ab0. guys what did you do?







#set the state back to 4, and some peyj states (after loading):
patch3=base+300
patch(patch3-4,0x90909090,4) # just for lisibility for debug
frm3=0x9f87f8 # this is (very probably) jade's control function, seems like a good place..? maybe not
seek=frm3
jmp(patch3) # deviation from original code
seek=patch3
call(0xae6610) # do the original call that we just smashed

#set *(*0xb80664+4)=4
wp(0xa1) # use eax
wp(0xb80664,4)
wp(0x00f883,3) # if null pointer, dont do the patch
wp(0x0674,2)
wp(0x04047880,4) # only apply the patch if *(eax+4)==4 : we need to do it once the loading is finished, and only one time
wp(0x0574,2) # else continue
bigjmp=seek
jmp(frm3+5)
#wp(0x90909090,4)
#wp(0x040440c6,4) # *(eax+4)=4
wp(0x000440c6,4) # *(eax+4)=0
#wp(0xff0440c6,4) # *(eax+4)=0xff ?

#set **(*(*(*0xb89cf8+0x18)+4)+0x44)=0x1e
wp(0xa1) # we can use eax,ecx,edx bcz it will not interfere afterwards
wp(0xb89cf8,4)
wp(0x00f883,3) # if null pointer, stop..
wp(0x74)
wp(bigjmp-seek-1) # use the big jmp that is before
wp(0x18408b,3)
wp(0x04408b,3) # eax=*(*(*0xb89cf8+0x18)+4)
wp(0x44488b,3) # ecx=*(eax+0x44)
wp(0x1e01c6,3) # *ecx=0x1e


#now do these setups (to be done after loading):
#set   *(*(*(*0xb89cf8+0x18)+4)+4*8)=*0xb80e68
wp(0x158b,2) # edx=*
wp(0xb80e68,4) # NOOOO! this is sometimes 0 :( but it should be set to something elsewhere bcz when i do this manually after the loading it works
wp(0x00fa83,3) # if edx==0,
wp(0x1674,2) # then ignore this patch
wp(0x205089,3) # *(eax+4*8)=edx
#set *(*(*(*(*0xb89cf8+0x18)+4)+4*8)+4*4)=0xa089f0
#        <=>       set *( *0xb80e68 +4*4)=0xa089f0
wp(0x1042c7,3) # *(edx+0x10)=
wp(0xa089f0,4) #todo: try without this, i'm not sure this is necessary

#set *(*(*(*(*0xb89cf8+0x18)+4)+0x44)+0x84)=*(*(*(*(*0xb89cf8+0x18)+4)+0x44)+0x204)
wp(0x00000204918b,6) # edx=*(ecx+0x204)
wp(0x000000849189,6) # *(ecx+0x84)=edx


jmp(frm3+5) # jmp back to normal code



# write resulting binary:
nf=open("bge_patched.exe","wb")
nf.write(bytes(patched))
nf.close()
