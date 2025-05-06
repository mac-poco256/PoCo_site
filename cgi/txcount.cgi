#!/usr/local/bin/perl

#��������������������������������������������������������������������
#��  TEXT COUNTER v2.0 (2002/09/17)
#��  ���v���e�L�X�g�J�E���^ (SSI��)
#��  Copyright(C) Kent Web 2002
#��  webmaster@kent-web.com
#��  http://www.kent-web.com/
#��������������������������������������������������������������������
$ver = 'TEXT COUNTER v2.0';
#��������������������������������������������������������������������
#�� [���ӎ���]
#�� 1. ���̃X�N���v�g�̓t���[�\�t�g�ł��B���̃X�N���v�g���g�p����
#��    �����Ȃ鑹�Q�ɑ΂��č�҂͈�؂̐ӔC�𕉂��܂���B
#�� 2. �ݒu�Ɋւ��鎿��̓T�|�[�g�f���ɂ��肢�������܂��B
#��    ���ڃ��[���ɂ�鎿��͈�؂��󂯂������Ă���܂���B
#��������������������������������������������������������������������
#
# [�^�O�̋L�q��]
#
# <!--#exec cgi="./cgi-bin/txcount.cgi"-->
#
#
# [�f�B���N�g���\����]
#
# public_html / index.html �� �����Ƀ^�O�L�q�F�J�E���^�\��
#     |
#     +-- cgi-bin / txcount.cgi [755]
#            |      txcount.tmp [644]
#            |      txcount.log [666]
#            |      txcount.txt [666]
#            |
#            +-- lock [777] /
#
#    ���e���v���[�g�t�@�C���utxcount.tmp�v���g�p���Ȃ��ꍇ�ɂ�
#      �utxcount.tmp�v�͕s�v (�t�@�C�������݂��Ȃ���Ύ����I��
#       �e�L�X�g�\�����܂��j
#
# [�`�F�b�N���[�h]
#
# �����Ɂucheck�v�����ČĂяo��
#
# ��Fhttp://�`�`/txcount.cgi?check


#============#
#  �ݒ荀��  #
#============#

# ���O�t�@�C��
$logfile = './txcount.log';

# �����t�@�C��
$dayfile = './txcount.txt';

# �e���v���[�g�t�@�C��
$tmpfile = './txcount.tmp';

# ���� (0 �̏ꍇ�����w��Ȃ��j
$digit = 0;

# 3����؂�\�� (0=no 1=yes)
# �� �J�E���^�l4���ȏ�ŗL��
$divide = 0;

# ���b�N�t�@�C���@�\
#  0 : �Ȃ�
#  1 : ���� �� symlink�֐���
#  2 : ���� �� mkdir�֐����iWinNT�T�[�o�Ȃ� symlink���g�p�ł��Ȃ����p�j
$lockkey = 1;

# ���b�N�t�@�C����
$lockfile = './lock/lock.dat';

# IP�A�h���X�`�F�b�N (0=no 1=yes)
# �� �d���J�E���g����
$ip_check = 0;

#============#
#  �ݒ芮��  #
#============#

# �`�F�b�N���[�h
if ($ENV{'QUERY_STRING'} eq "check") { &check; }

# IP�A�h���X�擾
$addr = $ENV{'REMOTE_ADDR'};

# �w�b�_�o��
print "Content-type: text/plain\n\n";

# ���b�N�J�n
$lockflag=0;
&lock if ($lockkey);

# �L�^���O
open(IN,"$logfile") || &error("Open Error $logfile");
$data1 = <IN>;
close(IN);
($count, $ip) = split(/:/, $data1);

# �������O
open(IN,"$dayfile") || &error("Open Error $dayfile");
$data2 = <IN>;
close(IN);
($day, $yes, $tod) = split(/:/, $data2);

# IP�`�F�b�N�i�d���J�E���g�h�~�j
unless ($ip_check && $addr eq $ip) {

	# �L�^���O
	$count++;
	open(OUT,">$logfile") || &error("Write Error $logfile");
	print OUT "$count\:$addr";
	close(OUT);

	# �{���̓����擾
	$ENV{'TZ'} = "JST-9";
	$mday = (localtime(time))[3];

	# ���ւ��̏ꍇ
	if ($day != $mday) {
		$yes = $tod;
		$tod = 0;
	}

	# �������O
	$tod++;
	open(OUT,">$dayfile") || &error("Write Error $dayfile");
	print OUT "$mday\:$yes\:$tod";
	close(OUT);
}

# ���b�N����
&unlock if ($lockkey);

if (length($count) > 3) { $lenflag=1; }
else { $lenflag=0; }

# ��������
if ($digit != 0) {
	while(length($count) < $digit) { $count = '0' . $count; }
}

# ����؂�
if ($divide) {
	if ($lenflag) { $count = &divide($count); }
	$yes = &divide($yes);
	$tod = &divide($tod);
}

# �e���v���[�g�ǂݍ���
open(IN,"$tmpfile") || &error("Open Error $tmpfile");
while (<IN>) {
	s/<!-- count -->/$count/;
	s/<!-- yesterday -->/$yes/;
	s/<!-- today -->/$tod/;

	print;
}
close(IN);
exit;

#--------------#
#  �G���[����  #
#--------------#
sub error {
	&unlock if ($lockflag);

	print "ERROR : $_[0]";
	exit;
}

#--------------#
#  ���b�N����  #
#--------------#
sub lock {
	# 1���ȏ�Â����b�N�͍폜����
	if (-e $lockfile) {
		local($mtime) = (stat($lockfile))[9];
		if ($mtime < time - 60) { &unlock; }
	}
	local($retry)=5;
	# symlink�֐������b�N
	if ($lockkey == 1) {
		while (!symlink(".", $lockfile)) {
			if (--$retry <= 0) { &error('LOCK is BUSY'); }
			sleep(1);
		}
	# mkdir�֐������b�N
	} elsif ($lockkey == 2) {
		while (!mkdir($lockfile, 0755)) {
			if (--$retry <= 0) { &error('LOCK is BUSY'); }
			sleep(1);
		}
	}
	$lockflag=1;
}

#--------------#
#  ���b�N����  #
#--------------#
sub unlock {
	if ($lockkey == 1) { unlink($lockfile); }
	elsif ($lockkey == 2) { rmdir($lockfile); }
	$lockflag=0;
}

#----------------#
#  ����؂菈��  #
#----------------#
sub divide {
	local($_) = $_[0];
	1 while s/(.*\d)(\d\d\d)/$1,$2/;
	$_;
}

#------------------#
#  �`�F�b�N���[�h  #
#------------------#
sub check {
	print "Content-type: text/html\n\n",
	"<html><head><title>$ver</title></head>\n",
	"<body><h2>Check Mode : $ver</h2><UL>\n";

	local($i)=0;
	foreach ($logfile, $dayfile, $tmpfile) {
		$i++;

		# �p�X
		if (-e $_) {
			print "<LI>�p�X�F$_ �� OK\n";

			# �p�[�~�b�V����
			if ($i < 3) {
				if (-r $_ && -w $_) {
					print "<LI>�p�[�~�b�V�����F$_ �� OK\n";
				} else {
					print "<LI>�p�[�~�b�V�����F$_ �� NG\n";
				}
			}
		} else {
			print "<LI><LI>�p�X�F$_ �� NG\n";
		}
	}

	# ���b�N�f�B���N�g��
	print "<LI>���b�N�`���F";
	if ($lockkey == 0) { print "���b�N�ݒ�Ȃ�\n"; }
	else {
		if ($lockkey == 1) { print "symlink\n"; }
		else { print "mkdir\n"; }

		($lockdir) = $lockfile =~ /(.*)[\\\/].*$/;
		print "<LI>���b�N�f�B���N�g���F$lockdir\n";

		if (-d $lockdir) {
			print "<LI>���b�N�f�B���N�g���̃p�X�FOK\n";

			if (-r $lockdir && -w $lockdir && -x $lockdir) {
				print "<LI>���b�N�f�B���N�g���̃p�[�~�b�V�����FOK\n";
			} else {
				print "<LI>���b�N�f�B���N�g���̃p�[�~�b�V�����FNG �� $lockdir\n";
			}
		} else {
			print "<LI>���b�N�f�B���N�g���̃p�X�FNG �� $lockdir\n";
		}
	}

	print "</UL>\n</body></html>\n";
	exit;
}

__END__

