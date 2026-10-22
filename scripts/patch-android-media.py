#!/usr/bin/env python3
"""Patch a freshly generated Capacitor Android project with a native media session service."""
from pathlib import Path
import re
root = Path('android')
if not root.exists():
    raise SystemExit('Android project not generated; run npx cap add android first.')
config = Path('capacitor.config.json').read_text()
m = re.search(r'"appId"\s*:\s*"([^"]+)"', config)
package = m.group(1) if m else 'vn.nhacmix.player'
java_dir = root / 'app/src/main/java' / Path(*package.split('.'))
java_dir.mkdir(parents=True, exist_ok=True)
plugin = '''package PACKAGE_NAME;

import android.Manifest;
import android.content.Intent;
import android.content.pm.PackageManager;
import android.os.Build;
import androidx.core.content.ContextCompat;
import com.getcapacitor.JSObject;
import com.getcapacitor.Plugin;
import com.getcapacitor.PluginCall;
import com.getcapacitor.PluginMethod;
import com.getcapacitor.annotation.CapacitorPlugin;

@CapacitorPlugin(name = "NhacMixMedia")
public class NhacMixMediaPlugin extends Plugin {
  static volatile NhacMixMediaPlugin instance;
  @Override public void load() { instance = this; }
  @PluginMethod public void start(PluginCall call) {
    ensureNotificationPermission();
    Intent i = new Intent(getContext(), NhacMixMediaService.class).setAction(NhacMixMediaService.ACTION_UPDATE);
    i.putExtra("title", call.getString("title", "NhacMix"));
    i.putExtra("artist", call.getString("artist", "Thư viện NhacMix"));
    i.putExtra("playing", call.getBoolean("isPlaying", true));
    ContextCompat.startForegroundService(getContext(), i); call.resolve();
  }
  @PluginMethod public void update(PluginCall call) {
    Intent i = new Intent(getContext(), NhacMixMediaService.class).setAction(NhacMixMediaService.ACTION_UPDATE);
    i.putExtra("title", call.getString("title", "NhacMix"));
    i.putExtra("artist", call.getString("artist", "Thư viện NhacMix"));
    i.putExtra("playing", call.getBoolean("isPlaying", true));
    ContextCompat.startForegroundService(getContext(), i); call.resolve();
  }
  @PluginMethod public void stop(PluginCall call) {
    getContext().startService(new Intent(getContext(), NhacMixMediaService.class).setAction(NhacMixMediaService.ACTION_STOP)); call.resolve();
  }
  private void ensureNotificationPermission() {
    if (Build.VERSION.SDK_INT >= 33 && getContext().checkSelfPermission(Manifest.permission.POST_NOTIFICATIONS) != PackageManager.PERMISSION_GRANTED) {
      getActivity().requestPermissions(new String[]{Manifest.permission.POST_NOTIFICATIONS}, 7731);
    }
  }
  static void dispatch(String action) {
    NhacMixMediaPlugin p = instance;
    if (p != null) { JSObject data = new JSObject(); data.put("action", action); p.notifyListeners("mediaAction", data); }
  }
}
'''.replace('PACKAGE_NAME', package)
(java_dir / 'NhacMixMediaPlugin.java').write_text(plugin)
service = '''package PACKAGE_NAME;

import android.app.Notification;
import android.app.NotificationChannel;
import android.app.NotificationManager;
import android.app.PendingIntent;
import android.app.Service;
import android.content.Intent;
import android.os.Build;
import android.os.IBinder;
import androidx.core.app.NotificationCompat;
import androidx.media.app.NotificationCompat.MediaStyle;
import android.support.v4.media.MediaMetadataCompat;
import android.support.v4.media.session.MediaSessionCompat;
import android.support.v4.media.session.PlaybackStateCompat;

public class NhacMixMediaService extends Service {
  public static final String ACTION_UPDATE="vn.nhacmix.media.UPDATE", ACTION_STOP="vn.nhacmix.media.STOP", ACTION_PLAY="vn.nhacmix.media.PLAY", ACTION_PAUSE="vn.nhacmix.media.PAUSE", ACTION_NEXT="vn.nhacmix.media.NEXT", ACTION_PREVIOUS="vn.nhacmix.media.PREVIOUS";
  private static final String CHANNEL="nhacmix_playback"; private static final int NOTIFICATION_ID=6204;
  private MediaSessionCompat session; private String title="NhacMix", artist="Thư viện NhacMix"; private boolean playing=false;
  @Override public void onCreate() {
    super.onCreate(); createChannel(); session = new MediaSessionCompat(this,"NhacMixSession");
    session.setFlags(MediaSessionCompat.FLAG_HANDLES_MEDIA_BUTTONS | MediaSessionCompat.FLAG_HANDLES_TRANSPORT_CONTROLS);
    session.setCallback(new MediaSessionCompat.Callback() {
      @Override public void onPlay(){dispatch("play");playing=true;refresh();}
      @Override public void onPause(){dispatch("pause");playing=false;refresh();}
      @Override public void onStop(){dispatch("stop");playing=false;stopForeground(true);stopSelf();}
      @Override public void onSkipToNext(){dispatch("next");}
      @Override public void onSkipToPrevious(){dispatch("previous");}
    }); session.setActive(true);
  }
  @Override public int onStartCommand(Intent intent,int flags,int startId) {
    if(intent==null){stopSelf();return START_NOT_STICKY;} String action=intent.getAction();
    if(ACTION_STOP.equals(action)){if(intent.getBooleanExtra("fromNotification",false))dispatch("stop");playing=false;if(session!=null){session.setActive(false);session.release();session=null;}stopForeground(true);stopSelf();return START_NOT_STICKY;}
    if(ACTION_PLAY.equals(action)){dispatch("play");playing=true;} else if(ACTION_PAUSE.equals(action)){dispatch("pause");playing=false;} else if(ACTION_NEXT.equals(action)){dispatch("next");} else if(ACTION_PREVIOUS.equals(action)){dispatch("previous");}
    else if(ACTION_UPDATE.equals(action)){if(intent.hasExtra("title"))title=intent.getStringExtra("title");if(intent.hasExtra("artist"))artist=intent.getStringExtra("artist");playing=intent.getBooleanExtra("playing",playing);}
    refresh(); return START_STICKY;
  }
  private void createChannel(){if(Build.VERSION.SDK_INT>=26){NotificationChannel c=new NotificationChannel(CHANNEL,"NhacMix playback",NotificationManager.IMPORTANCE_LOW);c.setDescription("Điều khiển phát nhạc NhacMix");((NotificationManager)getSystemService(NOTIFICATION_SERVICE)).createNotificationChannel(c);}}
  private PendingIntent actionIntent(String action,int request){Intent i=new Intent(this,NhacMixMediaService.class).setAction(action);if(ACTION_STOP.equals(action))i.putExtra("fromNotification",true);int flags=PendingIntent.FLAG_UPDATE_CURRENT|(Build.VERSION.SDK_INT>=23?PendingIntent.FLAG_IMMUTABLE:0);return PendingIntent.getService(this,request,i,flags);}
  private void refresh(){if(session==null)return;session.setMetadata(new MediaMetadataCompat.Builder().putString(MediaMetadataCompat.METADATA_KEY_TITLE,title).putString(MediaMetadataCompat.METADATA_KEY_ARTIST,artist).putString(MediaMetadataCompat.METADATA_KEY_ALBUM,"NhacMix").build());long actions=PlaybackStateCompat.ACTION_PLAY|PlaybackStateCompat.ACTION_PAUSE|PlaybackStateCompat.ACTION_PLAY_PAUSE|PlaybackStateCompat.ACTION_STOP|PlaybackStateCompat.ACTION_SKIP_TO_NEXT|PlaybackStateCompat.ACTION_SKIP_TO_PREVIOUS;session.setPlaybackState(new PlaybackStateCompat.Builder().setActions(actions).setState(playing?PlaybackStateCompat.STATE_PLAYING:PlaybackStateCompat.STATE_PAUSED,PlaybackStateCompat.PLAYBACK_POSITION_UNKNOWN,playing?1f:0f).build());NotificationCompat.Builder b=new NotificationCompat.Builder(this,CHANNEL).setSmallIcon(android.R.drawable.ic_media_play).setContentTitle(title).setContentText(artist).setVisibility(NotificationCompat.VISIBILITY_PUBLIC).setOnlyAlertOnce(true).setOngoing(playing).addAction(android.R.drawable.ic_media_previous,"Trước",actionIntent(ACTION_PREVIOUS,1)).addAction(playing?android.R.drawable.ic_media_pause:android.R.drawable.ic_media_play,playing?"Tạm dừng":"Phát",actionIntent(playing?ACTION_PAUSE:ACTION_PLAY,2)).addAction(android.R.drawable.ic_media_next,"Tiếp",actionIntent(ACTION_NEXT,3)).addAction(android.R.drawable.ic_menu_close_clear_cancel,"Dừng",actionIntent(ACTION_STOP,5)).setStyle(new MediaStyle().setMediaSession(session.getSessionToken()).setShowActionsInCompactView(0,1,2));Intent launch=getPackageManager().getLaunchIntentForPackage(getPackageName());if(launch!=null){PendingIntent content=PendingIntent.getActivity(this,4,launch,PendingIntent.FLAG_UPDATE_CURRENT|(Build.VERSION.SDK_INT>=23?PendingIntent.FLAG_IMMUTABLE:0));b.setContentIntent(content);}startForeground(NOTIFICATION_ID,b.build());}
  private static void dispatch(String action){NhacMixMediaPlugin.dispatch(action);}
  @Override public IBinder onBind(Intent intent){return null;}
  @Override public void onDestroy(){if(session!=null){session.setActive(false);session.release();session=null;}super.onDestroy();}
}
'''.replace('PACKAGE_NAME', package)
(java_dir / 'NhacMixMediaService.java').write_text(service)
# Register plugin in Capacitor's generated MainActivity.
main_files = list(root.glob('app/src/main/java/**/MainActivity.java')) + list(root.glob('app/src/main/java/**/MainActivity.kt'))
if not main_files: raise SystemExit('MainActivity not found in generated project')
p = main_files[0]; s = p.read_text()
if 'NhacMixMediaPlugin' not in s:
  if p.suffix == '.java':
    s = s.replace('import com.getcapacitor.BridgeActivity;', 'import com.getcapacitor.BridgeActivity;\nimport %s.NhacMixMediaPlugin;' % package)
    s = s.replace('public class MainActivity extends BridgeActivity {', 'public class MainActivity extends BridgeActivity {\n    @Override public void onCreate(android.os.Bundle savedInstanceState) { registerPlugin(NhacMixMediaPlugin.class); super.onCreate(savedInstanceState); }')
  else:
    s = s.replace('import com.getcapacitor.BridgeActivity', 'import com.getcapacitor.BridgeActivity\nimport %s.NhacMixMediaPlugin' % package)
    s = s.replace('class MainActivity : BridgeActivity()', 'class MainActivity : BridgeActivity() { override fun onCreate(savedInstanceState: android.os.Bundle?) { registerPlugin(NhacMixMediaPlugin::class.java); super.onCreate(savedInstanceState) } }')
  p.write_text(s)
# Permissions and service registration
manifest = root / 'app/src/main/AndroidManifest.xml'; s = manifest.read_text()
for perm in ['android.permission.FOREGROUND_SERVICE','android.permission.FOREGROUND_SERVICE_MEDIA_PLAYBACK','android.permission.POST_NOTIFICATIONS']:
  if perm not in s: s = s.replace('<application', f'<uses-permission android:name="{perm}" />\n    <application', 1)
if 'NhacMixMediaService' not in s:
  s = s.replace('</application>', f'<service android:name="{package}.NhacMixMediaService" android:exported="false" android:foregroundServiceType="mediaPlayback" />\n    </application>')
manifest.write_text(s)
# MediaSessionCompat dependency
build = root / 'app/build.gradle'; s = build.read_text()
if 'androidx.media:media:' not in s: s = s.replace('dependencies {', 'dependencies {\n    implementation "androidx.media:media:1.7.0"\n', 1)
s = re.sub(r'versionCode\s+\d+', 'versionCode 15', s, count=1)
s = re.sub(r'versionName\s+"[^"]+"', 'versionName "1.5.0"', s, count=1)
build.write_text(s)
